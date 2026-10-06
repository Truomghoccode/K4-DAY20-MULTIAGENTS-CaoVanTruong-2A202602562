"""GUIDE Phần 6d (mở rộng, tùy chọn) - subagent tự định nghĩa có skill.

Điều kiện `subagents-skills` = điều kiện `subagents` + bộ skill đóng băng `skills/auto` được chép vào sandbox và
khóa `"skills": ["/skills/"]` được thêm vào MỖI subagent tự định nghĩa. Tác tử chính KHÔNG nhận skill (không có
SKILLS_NOTE), nên so với `subagents` chỉ có một biến thay đổi: subagent có tri thức thủ tục hay không.

Chạy:  python -m lab.extension --tasks eval        -> results/subagents-skills/<task>/run.json
Không đổi `CONDITIONS`, `get_subagents()` hay `build_agent` cho các điều kiện chính thức: chỉ vá trong tiến trình này.
"""
import sys

from . import agent, runner

CONDITION = "subagents-skills"


def main(argv=None):
    plain_subagents, plain_build = agent.get_subagents, runner.build_agent
    agent.get_subagents = lambda: [{**s, "skills": ["/skills/"]} for s in plain_subagents()]
    # run_task bật use_skills khi có skills_dir; ép tắt để tác tử chính giữ nguyên như điều kiện `subagents`.
    runner.build_agent = lambda sandbox, mode, use_skills=False, model=None: plain_build(sandbox, mode, False, model)
    runner.CONDITIONS[CONDITION] = {"mode": "subagents", "skills_dir": "skills/auto"}
    runner.main(["--condition", CONDITION, *(sys.argv[1:] if argv is None else argv)])


if __name__ == "__main__":
    main()
