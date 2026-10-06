# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Cao Văn Trường| 2A202602562 | Toàn bộ (cá nhân) |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash-lite` (Google AI Studio, free tier: 15 RPM, 250k TPM, 500 RPD), `LAB_TEMPERATURE=0`, `recursion_limit=60`. Mọi lần gọi mô hình đi qua `make_robust_model()` trong `src/lab/agent.py`: giới hạn 14 RPM / 240k TPM, timeout 180 giây, thử lại tối đa 6 lần khi gặp lỗi tạm thời (429/5xx). Cơ chế này không đổi prompt hay mô hình, chỉ giảm nhiễu hạ tầng.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, langchain 1.4.3, langchain-google-genai 4.4.0; Windows 11, chạy trực tiếp trong conda env `aivn` (Python 3.11.16). Vì `LocalShellBackend` trên Windows dùng `cmd.exe`, `make_backend` chuyển lệnh của tác tử qua Git Bash (`_GitBashBackend`) để giữ ngữ nghĩa `/bin/sh` như trên Linux; env của shell chỉ gồm `PATH` (Python của env + Git usr/bin + System32), `HOME`/`USERPROFILE` = sandbox, `PYTHONDONTWRITEBYTECODE`, `PYTHONIOENCODING`, `SYSTEMROOT` (không có khóa API).
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): `subagents` **không** cao điểm hơn `baseline` trên tác vụ đánh giá (chênh lệch tối đa ±1 check mỗi tác vụ) nhưng tốn khoảng **2-3 lần token**. Căn cứ: trên tập học, check kỹ thuật của baseline đã đạt 18/18 nên không còn chỗ cho subagent cải thiện, còn 9/9 lỗi thuộc nhóm E (quy ước không nằm trong workspace) mà subagent cũng không thể biết; subagents đạt 17/27 so với 18/27, token ×2,3, và việc giao việc còn làm mất thông tin (data-learn lần 1 mất tên khóa). Tài liệu: hệ thống đa tác tử của Anthropic ghi nhận chi phí khoảng 15 lần hội thoại thường; lợi ích chủ yếu ở tác vụ cần khám phá song song, còn các tác vụ ở đây là tuần tự và nhỏ.
- H2 (skills-auto so với baseline): `skills-auto` đạt điểm **cao nhất** trên tác vụ đánh giá, nhưng lợi ích chỉ đến từ check quy ước mà skill đã chứa và quy ước đó **lặp lại** ở tác vụ đánh giá. Dự đoán: code-eval tăng nếu quy ước Python của Acme (type hint, `tests/test_regressions.py`, CHANGELOG) giữ nguyên; logs-eval tăng một phần (tên service, sắp xếp, schema header nếu giữ nguyên) nhưng **không** đạt các quy ước log-triage mới; data-eval **không** tăng vì bộ skill đóng băng không có skill dữ liệu (bị bộ lọc rò rỉ loại). Check kỹ thuật không đổi vì skill không chứa quy trình kỹ thuật mới. Căn cứ: trên tập học, skill nâng code-learn 7→10 và logs-learn 6→9 nhưng data-learn giữ 5/8. Tài liệu: SkillsBench ghi nhận skill do mô hình tự sinh trung bình không có lợi, còn SkillEvolBench ghi nhận lợi ích trên tác vụ học thường không chuyển sang tác vụ mới; ở đây lợi ích chỉ chuyển được tới đâu quy ước trùng tới đó.
- H3 (tác vụ học so với tác vụ đánh giá): điểm trên tác vụ đánh giá **thấp hơn hoặc bằng** tác vụ học ở cả ba điều kiện, và khoảng cách lớn nhất ở `skills-auto` (học 24/27 ở Phần 3.4; dự đoán đánh giá thấp hơn rõ rệt). Lý do: (1) quy ước của tác vụ đánh giá có thể mới hoặc khác chi tiết, và skill chép quy ước của tác vụ học là một dạng quá khớp; (2) tác vụ đánh giá có thêm bẫy kỹ thuật mới (ví dụ ranh giới tháng theo UTC, cấp độ log `SEVERE`/`FATAL`, dấu phân tách ` | `), nên check kỹ thuật cũng có thể giảm; (3) phản hồi `detail` của tác vụ đánh giá luôn rỗng nên không có kênh học nào trên đó.

## 3. Làm quen Deep Agents (Phần 0.3)

1. `scripts/tour.py` liệt kê 9 công cụ mặc định: công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; shell `execute`; giao việc `task`. Công cụ chạy lệnh shell là `execute`.
2. Subagent mặc định `general-purpose` có cùng bộ công cụ với tác tử chính nhưng ngữ cảnh bị cô lập: mỗi lần gọi là stateless, chỉ nhìn thấy prompt mà tác tử chính gửi qua `task`, và trả về một báo cáo cuối duy nhất (báo cáo này không hiện cho người dùng, tác tử chính phải tự tóm tắt lại).
3. Mô tả `task`: *"Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return."* Mô tả `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."* System prompt mặc định rỗng (`''`) khi không truyền `system_prompt=`, nên mọi quy ước (đường dẫn tương đối, tóm tắt trung thực) đến từ `BASE_PROMPT` của lab.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

Kết quả `baseline` trên tác vụ học: code-learn 7/10, data-learn 5/8, logs-learn 6/9 (18/27). Không lần chạy nào có `error`; `subagent_calls = 0` ở cả ba (tác tử mặc định không dùng `general-purpose`).

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `rule_type_hints` | E | `detail`: *"every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value."* Năm `edit_file` của tác tử chỉ sửa thân `parse_price`, `apply_discount`, `low_stock`, CSV quoting; không thêm annotation nào. |
| code-learn | `rule_regression_tests` | E | `detail`: *"add tests/test_regressions.py with one test function per bug you fixed (at least 3)"*. Không có `write_file` nào; câu kết: *"All 6 visible tests pass."* |
| code-learn | `rule_changelog` | E | `detail`: *"record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): …'"*. Tác tử có `read_file /workspace/CHANGELOG.md` (thấy sẵn mục `## Unreleased` rỗng) nhưng không ghi gì. |
| data-learn | `rule_money_in_cents` | E | `detail`: *"money values in answer.json are integer cents (1606.67 USD is written 160667)"*. Tác tử ghi doanh thu dạng USD thập phân, đúng chữ `(number)` của đề. |
| data-learn | `rule_meta_block` | E | `detail`: *"answer.json has an object `meta` = {source, rows_in, rows_used}"*. Tác tử chạy `glob "*"` trên `workspace` (kết quả: chỉ `README.md`, `sales.csv`), không tìm thấy quy ước nên chỉ ghi 5 khóa. |
| data-learn | `rule_clean_csv` | E | `detail`: *"write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents"*. Câu kết chỉ nêu *"Created `workspace/answer.json`"*. |
| logs-learn | `rule_service_names` | E | `detail`: *"service names … lower-case with '-' replaced by '_'"*. Tác tử giữ `payment-service` như ví dụ trong đề. |
| logs-learn | `rule_sorted_errors` | E | `detail`: *"`errors` is sorted by service, then by timestamp_utc, ascending"*. Script giữ thứ tự xuất hiện trong log. |
| logs-learn | `rule_schema_header` | E | `detail`: *"the top-level object has "schema_version": 2 and "generated_by": "log-triage""*. Đầu ra chỉ có `errors` và `counts_by_service` đúng như ví dụ JSON trong đề. |

Nhận xét:

- **Nhóm E chiếm 9/9 check thất bại.** Nguyên nhân chung: đề chỉ nói *"plus whatever the Acme … conventions require"*, còn quy ước không có trong workspace (data-learn: `glob` chỉ thấy README và dữ liệu). Tác tử làm đúng mọi điều được nêu tường minh rồi dừng; nó không có nguồn nào để biết quy ước, nên đây là thiếu tri thức của tổ chức chứ không phải cẩu thả.
- **Bằng chứng phủ định cho A-D** (`python scripts/check_breakdown.py`): check kỹ thuật `baseline` learn đạt **18/18**, check quy ước **0/9**. Tác tử đọc README/docstring (không có A), chạy lại pytest sau khi sửa (`visible_suite_passes` đạt, không có B), sửa cả caller khác (`other_caller_fixed`, không có C), xử lý đủ 3 định dạng ngày, offset múi giờ, `-999`, bản ghi trùng, traceback và `repeated N times` (không có D). Câu kết không khẳng định điều sai (không có F).
- **Skill phòng ngừa được nhóm E**: `detail` của tác vụ học phát biểu đúng quy tắc, curator có thể biến chúng thành checklist. Nhưng quy ước mỗi loại tác vụ khác nhau (tiền theo cent, khối `meta`, `clean.csv`, tên service, sắp xếp, header schema, type hint, test hồi quy, CHANGELOG), nên skill chỉ giúp tác vụ đánh giá khi quy ước ở đó trùng hoặc cùng dạng; quy ước hoàn toàn mới thì skill không biết.
- **Ghi chú hạ tầng (đã loại trước khi phân tích)**: (1) Git trên Windows (`core.autocrlf=true`) đã đổi `tasks/` sang CRLF, khiến `tests_not_modified` luôn thất bại do sai hash; thư mục `tasks/` được checkout lại với LF (nội dung y hệt git) và mọi lần chạy học được chạy lại. (2) Plugin `deepeval` trong env làm pytest của tác tử crash vì thiếu `USERPROFILE`; đã thêm biến này vào env của shell. (3) Các lần thử với Gemini và proxy Vyce bị loại vì hết quota và lỗi 504. Bảng trên chỉ dùng các lần chạy sạch.

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent đã định nghĩa** (`src/lab/subagents.py`), mỗi cái được nối thêm `PATHS_NOTE`:
  - `explorer`: đọc README, docstring, dữ liệu, log; báo cáo sự thật, **không sửa tệp**. Lý do: tách khâu tìm hiểu đặc tả (chống lỗi A) khỏi khâu sửa.
  - `implementer`: sửa code/dữ liệu trong `workspace/` và **phải chạy test hoặc script để kiểm chứng** trước khi báo cáo, nêu đúng tệp đã đổi. Lý do: chống lỗi B và F.
  - `reviewer`: kiểm tra độc lập ràng buộc, định dạng đầu ra, trường hợp biên; **không sửa tệp**. Lý do: góc nhìn thứ hai trước khi kết thúc.
- **`subagent_calls` và nhận xét**: code-learn **4**, data-learn **2**, logs-learn **2** (baseline: 0 ở cả ba). Tác tử chính giao việc ở cả ba tác vụ, khác baseline vốn không bao giờ gọi `general-purpose`, nên `SUBAGENTS_NOTE` cùng `description` rõ ràng đủ để kích hoạt việc giao việc. Ở code-learn và logs-learn, lời gọi `task` đầu tiên **hỏng định dạng** (mô hình chèn chuỗi rác `"} 代assistant to=functions.ls …"` vào tham số) và bị Deep Agents từ chối với *"Unexpected argument …; put all instructions for the subagent in `description`"*; tác tử gọi lại đúng ở lần sau. Như vậy 2/8 lời gọi `task` là lỗi định dạng của mô hình chứ không phải giao việc thật.
  - code-learn: chuỗi đúng thiết kế `explorer` → `implementer` → `reviewer`. Explorer chỉ ra chính xác 2 test lỗi và chỗ lệch docstring của `low_stock`; reviewer phát hiện CSV chưa quote ký tự xuống dòng và tác tử chính tự sửa thêm `export.py`. Điểm 7/10, bằng baseline (cùng trượt 3 check quy ước).
  - data-learn: tác tử chính gọi `implementer` hai lần. Lần 1 nó **diễn giải lại** yêu cầu thay vì chép tên khóa, subagent ghi các khóa tự đặt (`north_q1_2024_distinct_orders`, `whole_file_region_totals`, …) nhưng vẫn báo *"contains exactly the requested keys"* (nhóm F ở cấp subagent). Tác tử chính **đã kiểm tra** (`read_file workspace/answer.json`) và giao lại với danh sách khóa chính xác. Kết quả vẫn trượt `north_q1_orders` (subagent báo 13; baseline đạt check này): điểm **4/8, thấp hơn 5/8 của baseline**. Đây là một lỗi kỹ thuật nhóm D mới, phát sinh vì phép tính được làm lại trong ngữ cảnh rút gọn.
  - logs-learn: chỉ dùng `explorer` để tìm hiểu định dạng (báo cáo chính xác, nêu cả biến thể `error`/`Error`/`critical` và ba offset múi giờ), rồi tác tử chính tự viết parser. Điểm 6/9, bằng baseline.
- **Thông tin thiếu hoặc thừa khi giao việc**: lời giao việc thường đủ đường dẫn tương đối và ràng buộc kỹ thuật (*"Do not modify anything under workspace/tests/"*, *"treat -999 as missing"*), nhưng (1) ở data-learn lần 1 tên khóa đầu ra bị diễn giải lại nên mất; (2) không lời giao nào nêu được quy ước Acme vì chính tác tử chính cũng không biết (*"Follow Acme reporting conventions if discoverable in workspace"*; implementer trả lời *"No additional Acme reporting conventions were discoverable"*). Subagent không thể bù cho tri thức mà cả hệ thống không có, nên check quy ước vẫn 0/9.
- **Ảnh hưởng đến token và thời gian**: token trung bình mỗi tác vụ học **105.696** (subagents) so với **45.359** (baseline), tức **×2,3**; tổng thời gian 439 s so với 109 s (**×4**). Điểm học 17/27 so với 18/27: chi phí tăng hơn gấp đôi mà điểm không tăng (mất 1 check kỹ thuật vì lỗi khi giao việc ở data-learn).

## 6. Self-evolving: skill do curator sinh (Phần 3)

- **Số lần chạy curator, số skill bị xóa và lý do**: curator chạy **2 lần** trên `results/baseline` (chỉ `role == "learn"`).
  - Lần 1 sinh 3 skill hợp lệ về định dạng (`verify-repository-requirements`, `validate-data-pipelines`, `run-tests-from-project-root`). **Xóa cả 3**: (1) quá chung chung, không skill nào nêu cụ thể dù chỉ một trong 9 quy ước bị vi phạm (chỉ có câu kiểu *"verify units, ordering, and canonical forms"*, *"document each fix in the prescribed changelog format"*), nên tác tử đọc xong vẫn không biết tiền phải tính theo cent hay CHANGELOG phải có dạng `- fix(<function name>): …`, tức không thể phòng lỗi E; (2) `run-tests-from-project-root` nhắm vào lỗi môi trường (pytest không import được package) chứ không nhắm vào check nào bị chấm.
  - Nguyên nhân gốc nằm ở prompt curator: nó chỉ *cho phép* nêu tên do quy ước yêu cầu chứ không *đòi hỏi* chép quy ước. Prompt được bổ sung một quy tắc: chép mọi quy ước `RULE:` trong phản hồi thành chỉ dẫn cụ thể, nhóm theo loại tác vụ, cấm lời khuyên mơ hồ. Prompt không chứa bất kỳ thông tin nào của tác vụ đánh giá. Không sửa tay nội dung skill nào.
  - Lần 2 ghi **2 skill** (`code-change-compliance`, `log-triage-output`). Skill thứ ba (báo cáo dữ liệu) không được ghi. Lý do gần như chắc chắn là `validate_skill` loại nó vì chứa chuỗi `orders`, một phần của `eval_markers()` (tên tệp `orders.json` của data-eval), trong khi chính phản hồi của data-learn dùng từ này (*"rows_used: number of distinct orders with a known amount"*, *"one row per distinct order"*). Bộ lọc rò rỉ ở đây chặn nhầm tri thức hợp lệ của tác vụ học. Tôi không sửa prompt để né từ này, vì như vậy là dùng thông tin của tập đánh giá để thiết kế curator. Từ sau lần này, `curate_skills` in ra lý do mỗi khi loại skill để kiểm chứng.
  - Không chạy curator lần 3; bộ skill dùng để đóng băng là kết quả lần 2.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `code-change-compliance` | Tổng quát cho loại "sửa lỗi trong package Python": không nêu tên package, hàm, tệp nguồn hay con số của code-learn. Các tên cụ thể (`tests/test_regressions.py`, `CHANGELOG.md`, `## Unreleased`, `- fix(<function name>): …`) là chính quy ước Acme nên được phép. Ngưỡng "at least three" là con số của quy tắc, không phải đáp án. | Đúng, khớp từng ý với `detail` của `rule_type_hints`, `rule_regression_tests`, `rule_changelog`. Bước 5 (*"Do not treat a failed collection or 'no tests ran' as a passing check"*) rút từ vết, hợp lý. Rủi ro: nếu tác vụ mới dùng quy ước CHANGELOG hoặc tệp test khác, skill sẽ áp đặt sai định dạng. | 10 dòng (6 bước, có self-check). `description`: *"Use when fixing bugs or making changes in a Python package that has repository-level quality requirements."* Rộng vừa đủ. `skills_read`: được đọc ở code-learn (1) và cả data-learn. Code-learn đạt **10/10** (baseline 7/10). |
| `log-triage-output` | Tổng quát cho loại "trích lỗi từ log ra tệp có cấu trúc": không nêu tên tệp log, tên service hay số liệu. `errors`, `timestamp_utc`, `schema_version: 2`, `generated_by: "log-triage"` là quy ước nên được phép. | Đúng, khớp `detail` của `rule_service_names`, `rule_sorted_errors`, `rule_schema_header`. Khuyết điểm hình thức: dòng cuối thân skill là `=== END` (mô hình viết thiếu dấu `===`, parser giữ lại), vô hại nhưng không sạch. | 9 dòng (3 quy tắc + self-check). `description`: *"Use when extracting and summarizing errors from logs into a structured output file."* `skills_read`: đọc ở logs-learn (1) và data-learn. Logs-learn đạt **9/9** (baseline 6/9). |

Nhận xét về việc dùng skill ở Phần 3.4 (`results/skills-auto-dev`): `skills_read` lần lượt 1/2/1, `skills_modified = false` ở cả ba. Ở data-learn tác tử đọc **cả hai** skill (dù không skill nào nói về dữ liệu dạng bảng) vì `SKILLS_NOTE` yêu cầu đọc mọi skill *"whose description could apply"*; không có skill dữ liệu nên vẫn trượt đúng 3 check quy ước như baseline (5/8). Điều này khớp với dự đoán: skill chỉ sửa được các quy ước nó thực sự chứa.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
