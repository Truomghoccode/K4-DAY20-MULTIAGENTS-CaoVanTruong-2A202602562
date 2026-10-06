"""GUIDE Phần 1 - Dựng tác tử (agent) bằng Deep Agents.   >>> SINH VIÊN CÀI ĐẶT make_backend VÀ build_agent <<<

Pseudo-code: guides/pseudocode/01_agent.md
Kiểm tra:    pytest tests/test_02_agent.py
"""
import functools
import os
import shutil
import sys
import tempfile
import threading
import time
from collections import deque
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend

from .model import make_model
from .subagents import get_subagents

# ---- CÓ SẴN, KHÔNG SỬA: system prompt dùng chung cho mọi sinh viên (để đường cơ sở so sánh được) ----
PATHS_NOTE = (
    "PATHS: every path is relative to the sandbox root and never starts with '/'. "
    "The task files are in the folder workspace/ (for example workspace/app.log). "
    "Use exactly this relative form both in the file tools and in the shell (execute); "
    "the shell starts in the sandbox root. "
)
BASE_PROMPT = (
    "You are an engineering assistant working in a sandbox. "
    + PATHS_NOTE
    + "Use the shell to run Python and tests. "
    "When you are done, reply with a short summary that mentions only files you really created or changed."
)
SKILLS_NOTE = (
    " Skills are in the folder skills/ (one sub-folder per skill with a SKILL.md). "
    "As your FIRST action, read the SKILL.md of every skill whose description could apply to the task, "
    "then follow them. Never modify skills/."
)
SUBAGENTS_NOTE = (
    " You have specialised subagents (see the description of the task tool). "
    "For anything beyond a trivial step, delegate to a suitable subagent and put ALL the task rules and file paths "
    "in the delegation message, because a subagent sees only what you send. "
    "Check what a subagent returns before you rely on it."
)
# --------------------------------------------------------------------------------------------------


def make_backend(sandbox: Path):
    """Tạo backend (môi trường thực thi) cho tác tử.

    Yêu cầu:
      - Thư mục gốc (root_dir) là `sandbox`; đường dẫn tương đối `workspace/...` và `skills/...`
        phải dùng được ở CẢ công cụ tệp lẫn shell (shell chạy với thư mục làm việc = `sandbox`).
      - Tác tử chạy được lệnh shell và gọi được `python` (cần đặt PATH).
      - KHÔNG chuyển biến môi trường của bạn vào shell của tác tử (khóa API không được lộ).
    """
    py_dir = Path(sys.executable).parent
    if sys.platform != "win32":
        env = {"PATH": f"{py_dir}:/usr/local/bin:/usr/bin:/bin", "HOME": str(sandbox), "PYTHONDONTWRITEBYTECODE": "1"}
        return LocalShellBackend(root_dir=sandbox, virtual_mode=True, inherit_env=False, env=env, timeout=120)
    git = next(d for d in Path(shutil.which("git")).resolve().parents if (d / "usr" / "bin" / "bash.exe").exists())
    env = {
        "PATH": os.pathsep.join(map(str, [py_dir, py_dir / "Library" / "bin", py_dir / "Scripts",
                                          git / "usr" / "bin", Path(os.environ["SYSTEMROOT"]) / "System32"])),
        "HOME": str(sandbox),
        "USERPROFILE": str(sandbox),                                  # Path.home() on Windows reads this, not HOME
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "SYSTEMROOT": os.environ["SYSTEMROOT"],                       # Python on Windows cannot start without it
    }
    return _GitBashBackend(git / "usr" / "bin" / "bash.exe", root_dir=sandbox, virtual_mode=True, inherit_env=False,
                           env=env, timeout=120)


class _GitBashBackend(LocalShellBackend):
    """Windows only: LocalShellBackend runs commands via cmd.exe; route them through Git Bash so the agent gets
    the same POSIX shell (`&&`, quotes, `ls`, `cat`) as on Linux/macOS. The command goes through a temp script
    so cmd.exe never has to parse it."""
    # ponytail: Windows shim for running natively in conda; drop it when running under WSL/Docker.

    def __init__(self, bash: Path, **kwargs):
        super().__init__(**kwargs)
        self._bash = bash

    def execute(self, command, *, timeout=None):
        if not command or not isinstance(command, str):
            return super().execute(command, timeout=timeout)
        fd, script = tempfile.mkstemp(suffix=".sh")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(command)
        try:
            return super().execute(f'"{self._bash}" "{script}"', timeout=timeout)
        finally:
            os.unlink(script)


def make_robust_model():
    """make_model() hardened against flaky APIs: a 180 s timeout per request, rate limiting and retries of the
    whole call on transient errors (see `_with_retry`). Streaming stays off on purpose: a streaming model is
    called through `_stream`, which would bypass the retrying `_generate`."""
    m = make_model()
    if getattr(m, "timeout", 0) is None:                           # Gemini default: no timeout, a call once hung 98 min
        m.timeout = 180
    if os.getenv("LAB_REASONING_EFFORT"):                          # e.g. "none": OpenAI reasoning models reject
        m.reasoning_effort = os.environ["LAB_REASONING_EFFORT"]    # function tools on /chat/completions otherwise
    if getattr(m, "root_client", None) is not None:              # ChatOpenAI / AzureChatOpenAI: no timeout by default
        m.root_client = m.root_client.with_options(max_retries=6, timeout=180)
        m.client = m.root_client.chat.completions
    m.__class__ = _with_retry(type(m))                             # also covers subagents: they share this model
    return m


# Provider quota per minute, with a safety margin. Default = Gemini free tier (15 RPM, 250k input TPM);
# override with LAB_RPM / LAB_TPM in .env for another provider.
# ponytail: one in-process sliding window; runs started in parallel processes would not share it.
RPM_LIMIT, TPM_LIMIT = int(os.getenv("LAB_RPM", 14)), int(os.getenv("LAB_TPM", 240_000))
REQUEST_LOG = Path(tempfile.gettempdir()) / "lab_requests.log"   # one line per request, to watch the daily quota
_window: deque = deque()            # [start_time, input_tokens] of the requests of the last 60 s
_window_lock = threading.Lock()
_last_input = [0]                   # input tokens of the previous call = estimate for the next one


def _throttle() -> list:
    """Block until one more request fits in the RPM/TPM window, then reserve it."""
    with _window_lock:
        while True:
            now = time.time()
            while _window and now - _window[0][0] > 60:
                _window.popleft()
            if len(_window) < RPM_LIMIT and sum(t for _, t in _window) + _last_input[0] <= TPM_LIMIT:
                break
            time.sleep(max(0.5, 60.5 - (now - _window[0][0])))
        slot = [now, _last_input[0]]
        _window.append(slot)
    with open(REQUEST_LOG, "a", encoding="utf-8") as f:
        f.write(f"{now:.0f}\n")
    return slot


@functools.cache
def _with_retry(cls):
    """Subclass whose `_generate` is rate limited and retries the WHOLE call: a proxy sometimes aborts a stream
    half-way ("The request timed out"), which the client cannot retry by itself. 4xx errors other than 429 are
    real errors and are raised at once."""
    class Retrying(cls):
        def _generate(self, *args, **kwargs):
            for attempt in range(6):
                slot = _throttle()
                try:
                    result = super()._generate(*args, **kwargs)
                except Exception as e:  # noqa: BLE001
                    status = getattr(e, "status_code", None) or getattr(e, "code", None)
                    if attempt == 5 or (isinstance(status, int) and 400 <= status < 500 and status != 429):
                        raise
                    time.sleep(min(5 * 2 ** attempt, 60))
                    continue
                used = (getattr(result.generations[0].message, "usage_metadata", None) or {}).get("input_tokens", 0)
                slot[1] = _last_input[0] = used
                return result
    Retrying.__name__ = cls.__name__
    return Retrying


def build_agent(sandbox: Path, mode: str = "single", use_skills: bool = False, model=None):
    """Tạo tác tử Deep Agents.

    Tham số:
      sandbox:    thư mục chứa `workspace/` (và `skills/` nếu có).
      mode:       "single"    -> tác tử mặc định (có subagent `general-purpose` sẵn của Deep Agents)
                  "subagents" -> thêm các subagent từ `get_subagents()` (nối PATHS_NOTE vào `system_prompt` của MỖI subagent,
                                 vì subagent không nhận BASE_PROMPT) và thêm SUBAGENTS_NOTE vào prompt chính
      use_skills: True -> nạp thư mục "/skills/" qua tham số `skills=` của create_deep_agent
                  và thêm SKILLS_NOTE vào prompt.
      model:      mô hình ngôn ngữ; None -> dùng `make_model()`.
    mode không hợp lệ -> ném ValueError.
    Trả về: đồ thị (graph) đã biên dịch, gọi bằng `.invoke({"messages": [...]})`.
    """
    if mode not in {"single", "subagents"}:
        raise ValueError(f"unknown mode: {mode!r}")
    kwargs = {}
    prompt = BASE_PROMPT
    if mode == "subagents":
        kwargs["subagents"] = [{**sub, "system_prompt": sub["system_prompt"] + " " + PATHS_NOTE} for sub in get_subagents()]
        prompt += SUBAGENTS_NOTE
    if use_skills:
        kwargs["skills"] = ["/skills/"]
        prompt += SKILLS_NOTE
    return create_deep_agent(model=model or make_robust_model(), system_prompt=prompt, backend=make_backend(sandbox), **kwargs)
