"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": "Use when you need to inspect project structure, read documentation, search the codebase, "
                           "or inspect raw logs/data without modifying files.",
            "system_prompt": "You are a code and data exploration specialist. Read and analyze files thoroughly "
                             "(README, docstrings, CHANGELOG, data samples). Report precise facts, schema details, "
                             "conventions and root causes without making any file modifications.",
        },
        {
            "name": "implementer",
            "description": "Use when you need to write or edit source code, fix identified bugs, clean dirty datasets, "
                           "or execute scripts in the sandbox workspace.",
            "system_prompt": "You are an implementation specialist. Execute the required changes carefully in workspace/ "
                             "and run local tests or scripts to verify your implementation before reporting back. "
                             "Report exactly which files you created or changed.",
        },
        {
            "name": "reviewer",
            "description": "Use when work has been implemented and you need an independent verification of task "
                           "constraints, output format, edge cases, and regression tests.",
            "system_prompt": "You are a quality assurance reviewer. Verify that all task requirements and constraints "
                             "are satisfied, re-run tests, and check edge cases. Do not edit files; only report "
                             "findings and validation status.",
        },
    ]
