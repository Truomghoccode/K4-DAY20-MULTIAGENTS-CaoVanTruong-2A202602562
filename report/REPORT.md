# Báo cáo Lab: Self evolving Agentic


## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Cao Văn Trường| 2A202602562 | Toàn bộ (cá nhân) |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `google_genai:gemini-3.5-flash-lite` (Google AI Studio, free tier: 15 RPM, 250k TPM, 500 RPD), `LAB_TEMPERATURE=0`, `recursion_limit=60`. Mọi lần gọi mô hình đi qua `make_robust_model()` trong `src/lab/agent.py`: giới hạn 14 RPM / 240k TPM, timeout 180 giây, thử lại tối đa 6 lần khi gặp lỗi tạm thời (429/5xx). Cơ chế này không đổi prompt hay mô hình, chỉ giảm nhiễu hạ tầng.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, langchain 1.4.3, langchain-google-genai 4.4.0; Windows 11, chạy trực tiếp trong conda env `aivn` (Python 3.11.16). Vì `LocalShellBackend` trên Windows dùng `cmd.exe`, `make_backend` chuyển lệnh của tác tử qua Git Bash (`_GitBashBackend`) để giữ ngữ nghĩa `/bin/sh` như trên Linux; env của shell chỉ gồm `PATH` (Python của env + Git usr/bin + System32), `HOME`/`USERPROFILE` = sandbox, `PYTHONDONTWRITEBYTECODE`, `PYTHONIOENCODING`, `SYSTEMROOT` (không có khóa API).
- Số lần chạy tác vụ đã dùng / ngân sách: 21 lần chạy chính thức (baseline 6, subagents 6, skills-auto 3 ở Phần 3.4 + 6 sau đóng băng) + 3 lần chạy thử thách 6d + 2 lần gọi curator; khoảng 1,9 triệu token với `gpt-6-luna` (không đặt ngân sách cứng; các lần chạy hỏng vì hạ tầng trước khi đổi sang OpenAI không tính).
- Commit của tag `freeze`: `5f4960454f3ae7b56dd853d469c69c9170c11bf7` (`freeze skills`), ngay sau commit `39a688b` (`hypotheses`).

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)


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

`python -m lab.compare > report/table.md`:

```text
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 10/10 |
| data-learn | 5/8 | 4/8 | 5/8 |
| logs-learn | 6/9 | 6/9 | 9/9 |
| code-eval | 7/11 | 7/11 | 10/11 |
| data-eval | 5/9 | 4/9 | 4/9 |
| logs-eval | 6/10 | 6/10 | 9/10 |
| **Mean score - learning tasks** | 0.66 | 0.62 | 0.88 |
| **Mean score - evaluation tasks** | 0.60 | 0.56 | 0.75 |
| **Mean tokens per run** | 39,945 | 104,368 | 43,553 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |
```

`python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12          34,530      0/3
baseline      learn    18/18         0/9           45,359      0/3
subagents     eval     17/18         0/12         103,041      0/3
subagents     learn    17/18         0/9          105,696      0/3
skills-auto   eval     17/18         6/12          45,930      3/3
skills-auto   learn    18/18         6/9           41,175      3/3
```

`python scripts/verify_freeze.py` → `checked 6 runs of skill conditions: OK` (chạy với `PYTHONUTF8=1`: trên Windows, `git show` của báo cáo tiếng Việt bị giải mã bằng codepage `cp1258` và script lỗi `NoneType`; đây là vấn đề mã hóa của môi trường, không phải của quy trình đóng băng).

Không lần chạy chính thức nào có `error` khác `null`, và `skills_modified = false` ở mọi lần chạy. Các lần chạy bị loại trước đó (lỗi hạ tầng: Gemini hết quota, proxy 504, request treo, `tasks/` bị đổi sang CRLF) đã được lưu ra ngoài `results/` và không có trong bảng.

## 8. Phân tích

1. **Học và đánh giá.** So với `baseline` (học 0,66, đánh giá 0,60), chỉ `skills-auto` cải thiện ở **cả hai** tập: học 0,88 (+0,22), đánh giá 0,75 (+0,15). `subagents` không cải thiện tập nào (0,62 và 0,56; mỗi tập mất 1 check ở tác vụ dữ liệu). Không có điều kiện nào chỉ tăng ở tập học. Tuy vậy, mức tăng của `skills-auto` co lại khi sang tập đánh giá: học 24/27 nhưng đánh giá chỉ 23/30, vì mỗi tác vụ đánh giá có thêm một quy ước mới mà skill không biết. Đây là dấu hiệu **chuyển giao một phần**: skill khớp quy ước của tập học, phần quy ước trùng thì chuyển được, phần mới thì không. Điều này khớp H2, H3 và nhận định của SkillEvolBench.
2. **Check kỹ thuật và check quy ước.** Check kỹ thuật gần như bão hòa ở mọi điều kiện (18/18, 17/18, 17/18 trên đánh giá), nên toàn bộ mức tăng của `skills-auto` nằm ở check quy ước: 0/12 → **6/12** trên đánh giá, 0/9 → **6/9** trên học. Sáu check đánh giá đạt được chính là 3 quy ước code (`rule_type_hints`, `rule_regression_tests`, `rule_changelog`) và 3 quy ước log (`rule_service_names`, `rule_sorted_errors`, `rule_schema_header`), vốn **lặp lại y hệt** từ tác vụ học. Các check quy ước **mới** của tập đánh giá đều trượt ở cả 3 điều kiện: `rule_version_bump` (code-eval), `rule_source_line` (logs-eval), `rule_sorted_keys_format` (data-eval). Skill không giúp được vì chúng chỉ chép các quy tắc đã thấy trong `detail` của tác vụ học, còn tác vụ đánh giá không có `detail` và quy ước mới không suy ra được từ quy ước cũ. Data-eval còn trượt cả 3 quy ước cũ về dữ liệu, vì skill dữ liệu đã bị bộ lọc rò rỉ loại (mục 6).
3. **Một check được skill giúp và một check không được giúp.**
   - *Được giúp*: `rule_changelog` ở code-eval. Vết `results/skills-auto/code-eval/trace.md` cho thấy hành động đầu tiên là `read_file skills/code-change-compliance/SKILL.md` (`skills_read = 1`), sau đó tác tử `read_file workspace/CHANGELOG.md` ngay sau README, sửa 4 module, rồi `write_file workspace/tests/test_regressions.py` và cuối cùng `edit_file workspace/CHANGELOG.md`, đúng bước 3-4 của skill (*"Record every fix in `CHANGELOG.md` under `## Unreleased`, using bullets exactly in the form `- fix(<function name>): …`"*). Baseline code-eval chỉ thấy `CHANGELOG.md` trong kết quả `ls` mà không hề mở; khác biệt giữa hai lần chạy là skill.
   - *Không được giúp*: `rule_version_bump` ở code-eval. Tác tử có đọc `workspace/bookings/__init__.py` và làm theo **toàn bộ** skill (đạt 10/11), nhưng skill không có quy tắc tăng phiên bản vì tác vụ học không hề có check đó, tức **skill thiếu**. Ở data-eval, tác tử đọc nhầm `log-triage-output` (`skills_read = 1`) vì không có skill dữ liệu, nên vẫn trượt 4 quy ước dữ liệu (**skill thiếu**). Data-eval còn trượt thêm check kỹ thuật `march_orders_utc`: script của tác tử gọi `march.add(e['id'])` trước khi loại đơn thiếu `total`, nên đếm cả đơn không nằm trong doanh thu, trái với đề (*"orders counted in `march_revenue_utc`"*). Skill nó đọc không nói gì về phép đếm này, nên đây là biến thiên của mô hình (lỗi nhóm A/D) chứ không phải tác dụng của skill.
4. **Chi phí.** Token trung bình mỗi lần chạy: baseline 39.945, `skills-auto` 43.553 (+9%), `subagents` 104.368 (**×2,6**). Hiệu quả theo số check đạt trên 1.000 token, tính trên cả 6 tác vụ: `skills-auto` **0,180**, baseline 0,150, `subagents` 0,054. Theo trung bình điểm trên 1.000 token: 0,0187 / 0,0158 / 0,0057. `skills-auto` hiệu quả nhất: thêm khoảng 1 lần `read_file` và vài trăm token skill trong ngữ cảnh, đổi lại +11 check. Đa tác tử **không đáng chi phí** trong thí nghiệm này: tốn 2,6 lần token, gấp 3,2 lần thời gian (662 s so với 204 s), mà điểm thấp hơn baseline 2 check. Các tác vụ ở đây nhỏ và tuần tự, ngữ cảnh vừa một cửa sổ, nên việc chia nhỏ chỉ thêm chi phí truyền đạt và gây mất thông tin khi giao việc (mục 5).
5. **Rò rỉ dữ liệu và quá khớp.** Không có rò rỉ từ tập đánh giá. Curator chỉ đọc `run.json` có `role == "learn"` (test `test_curator_writes_only_valid_skills_and_never_leaks` kiểm tra prompt không chứa `data-eval` hay `march_orders_utc`); `detail` của tác vụ đánh giá luôn rỗng; `validate_skill` loại skill chứa `eval_markers()`; prompt curator được sửa ở lần 2 không dùng thông tin tập đánh giá. Ngược lại, bộ lọc còn **quá chặt**: skill dữ liệu bị loại chỉ vì từ thông dụng `orders` trùng tên tệp `orders.json` của data-eval, dù từ này đến từ phản hồi của data-learn. Về quá khớp: hai skill chép nguyên quy ước của tác vụ học, và mức tăng trên tập đánh giá đến **hoàn toàn** từ việc quy ước lặp lại; quy ước mới thì 0/3. Nếu tổ chức đổi định dạng CHANGELOG hay tên service, skill sẽ áp đặt quy tắc cũ, đúng kiểu quá khớp SkillEvolBench mô tả. Về tính tổng quát: skill không nêu tên package (`inventory`/`bookings`), hàm, tệp dữ liệu hay con số đáp án, và vẫn được kích hoạt đúng ở `bookings` (code-eval) và `worker.log` (logs-eval) mà curator chưa từng thấy.
6. **Nhiễu.** Cùng bộ skill (hash `bc6c2a7d…`) trên tác vụ học: trước đóng băng (Phần 3.4, `results/skills-auto-dev`) 10/10, 5/8, 9/9; sau đóng băng 10/10, 5/8, 9/9, **chênh lệch 0 check** ở cả ba tác vụ. Token dao động: 63.483 → 68.288 (+8%), 41.120 → 33.687 (−18%), 24.868 → 21.551 (−13%). Như vậy với `temperature=0`, điểm ổn định ở mức tác vụ, còn quỹ đạo (số bước, token) thay đổi đáng kể. Nhưng một cặp lần chạy chưa đủ để ước lượng phương sai: ví dụ `march_orders_utc` và `north_q1_orders` cho thấy cùng một mô hình có lúc đếm sai một phép tính mà lần khác làm đúng. Vì vậy chênh lệch ±1 check (baseline so với `subagents`, hay data-eval 5/9 so với 4/9) **nằm trong vùng nhiễu** và không nên diễn giải. Chênh lệch +6 check quy ước của `skills-auto`, lặp lại nhất quán ở cả học và đánh giá với cơ chế thấy rõ trong vết, thì vượt xa nhiễu.

## 9. Hạn chế và tính hợp lệ

1. **Cỡ mẫu rất nhỏ và mỗi cấu hình chạy một lần.** Mỗi vai trò chỉ có 3 tác vụ (30 check đánh giá), mỗi điều kiện một lần chạy. Ước lượng nhiễu ở 8.6 chỉ dựa trên 3 cặp lần chạy. Do đó chỉ kết luận được về các khác biệt lớn và có cơ chế rõ (+6 check quy ước của `skills-auto`); các khác biệt ±1 check giữa baseline và `subagents` không có ý nghĩa thống kê.
2. **Tác vụ và quy ước do giảng viên thiết kế.** Phần lớn điểm thiếu là quy ước Acme ẩn, được thiết kế để lặp lại giữa học và đánh giá (9/12 check quy ước của tập đánh giá trùng y hệt tập học). Điều này ưu ái `skills-auto` một cách cấu trúc; trong môi trường thực, nơi quy ước đa dạng hơn, mức tăng có thể nhỏ hơn nhiều, và 3 quy ước mới (0/3) là chỉ báo thực tế hơn cho khả năng tổng quát.
3. **Chỉ một mô hình, với cấu hình riêng.** Mọi lần chạy dùng `openai:gpt-6-luna` với `reasoning_effort=none` (bắt buộc để dùng function tools trên `/chat/completions`), `temperature=0`. Kết quả không chắc đúng cho mô hình có suy luận, cho mô hình yếu hơn (dễ hỏng tool call như 2/8 lời gọi `task` ở mục 5), hay cho mô hình khác hãng.
4. **Curator có tính ngẫu nhiên và đã được can thiệp một lần.** Lần 1 sinh skill vô dụng; lần 2 tốt sau khi sửa prompt. Một bộ skill khác (hoặc một lần chạy curator khác) có thể cho kết quả `skills-auto` rất khác, và chỉ hai lần chạy thì không ước lượng được phân phối chất lượng skill. Bộ lọc `eval_markers()` cũng loại nhầm skill dữ liệu, làm data-eval không có cơ hội cải thiện.
5. **Đo lường không thấy bên trong subagent.** `tool_calls`, `skills_read` chỉ đếm luồng chính, nên với `subagents` (và thử thách 6d) không biết subagent đọc gì hay chạy lệnh gì; nhận xét về subagent dựa vào lời giao việc và báo cáo cuối.
6. **Môi trường Windows thay vì Linux/Docker.** Shell của tác tử chạy qua Git Bash; phải sửa thêm `USERPROFILE` (plugin `deepeval`), timeout, line ending của `tasks/`. Kết quả cuối đã loại các lần chạy bị ảnh hưởng, nhưng nhóm khác chạy trên Linux có thể thấy hành vi shell hơi khác (ví dụ thông báo `Running teardown with pytest sessionfinish...` của `deepeval` vẫn xuất hiện trong vết).

## 10. Kết luận

Trên 6 tác vụ với `gpt-6-luna`, chỉ `skills-auto` cải thiện điểm (đánh giá 0,60 → 0,75; học 0,66 → 0,88) với chi phí token gần như không đổi (+9%), và toàn bộ mức tăng đến từ 6 check quy ước Acme mà skill chép từ phản hồi của tác vụ học rồi lặp lại ở tác vụ đánh giá. Ba quy ước mới của tập đánh giá trượt ở mọi điều kiện, nên skill tự sinh chuyển giao được đúng phần tri thức trùng lặp chứ không tổng quát hóa sang quy tắc chưa thấy. `subagents` tốn 2,6 lần token, 3,2 lần thời gian mà không tăng điểm (0,56 so với 0,60), vì các tác vụ nhỏ, tuần tự và việc giao việc làm mất thông tin. Đề xuất tiếp theo: giữ lại lời phát biểu quy ước dữ liệu bằng cách cho `validate_skill` so khớp marker theo ranh giới từ hoặc chỉ theo tên tệp đầy đủ (`orders.json`), rồi chạy lại mỗi điều kiện ít nhất 3 lần để ước lượng phương sai.

## Phụ lục

### A. Lệnh đã chạy (theo thứ tự, conda env `aivn`)

```bash
pytest                                                    # 29 passed (test_01 12, test_02 9, test_03 6, test_04 2)
python -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').text)"
python scripts/tour.py
git -c core.autocrlf=false checkout -- tasks/            # khôi phục line ending LF cho tasks/ (xem ghi chú C)
python -m lab.runner --condition baseline  --tasks learn
python -m lab.runner --condition subagents --tasks learn
python scripts/check_breakdown.py
python -m lab.curator                                     # lần 1: 3 skill, xóa cả 3 (mục 6)
python -m lab.curator                                     # lần 2 (prompt bổ sung): 2 skill
python -m lab.runner --condition skills-auto --tasks learn
cp -r results/skills-auto results/skills-auto-dev
git add report/REPORT.md && git commit -m "hypotheses"
git add -A && git commit -m "freeze skills" && git tag freeze
python -m lab.runner --condition baseline  --tasks eval
python -m lab.runner --condition subagents --tasks eval
python -m lab.runner --condition skills-auto --tasks all
PYTHONUTF8=1 python scripts/verify_freeze.py              # OK
python -m lab.compare > report/table.md
python scripts/check_breakdown.py
python -m lab.extension --tasks eval                      # thử thách 6d -> results/subagents-skills/
```

Cấu hình `.env` (không có khóa): `LAB_MODEL=openai:gpt-6-luna`, `LAB_TEMPERATURE=0`, `LAB_REASONING_EFFORT=none`, `LAB_RPM=60`, `LAB_TPM=1000000`.

### B. Thử thách mở rộng 6d: subagent có skill

**Thiết kế.** Điều kiện mới `subagents-skills` (`src/lab/extension.py`, kết quả trong thư mục riêng `results/subagents-skills/`) giống hệt `subagents`, chỉ khác một biến: bộ skill **đã đóng băng** `skills/auto` được chép vào sandbox và mỗi subagent tự định nghĩa nhận thêm `"skills": ["/skills/"]`. Tác tử chính **không** nhận skill (không có `skills=` và không có `SKILLS_NOTE`), nên mọi khác biệt so với `subagents` đến từ việc subagent có tri thức thủ tục. Module chỉ vá `get_subagents`/`build_agent` trong tiến trình của nó và không đổi `CONDITIONS` hay các điều kiện chính thức. Một kiểm tra ngoại tuyến (mô hình giả `ScriptedChatModel`) xác nhận system prompt của subagent có tên skill còn của tác tử chính thì không. Chạy trên 3 tác vụ đánh giá, sau tag `freeze`.

**Số liệu (tác vụ đánh giá).**

| Tác vụ | subagents | subagents-skills | skills-auto (tham chiếu) |
|---|---|---|---|
| code-eval | 7/11 | **9/11** | 10/11 |
| data-eval | 4/9 | 5/9 | 4/9 |
| logs-eval | 6/10 | **2/10** | 9/10 |
| Tổng / điểm trung bình | 17/30 / 0,56 | 16/30 / 0,52 | 23/30 / 0,75 |
| Check kỹ thuật | 17/18 | 14/18 | 17/18 |
| Check quy ước | 0/12 | 2/12 | 6/12 |
| Token (tổng 3 tác vụ) | 309.123 | 629.394 (×2,0) | 137.792 |
| Thời gian | 222 s | 561 s | 70 s |

**Phân tích cơ chế qua vết.** `skills_read` của luồng chính bằng 0 theo thiết kế (tác tử chính không có skill, việc subagent đọc skill không hiện trong vết), nên bằng chứng lấy từ báo cáo của subagent:

- *Skill có tác dụng bên trong subagent (code-eval, +2).* Lời giao việc cho `implementer` chỉ nêu lỗi nghiệp vụ (định dạng thời lượng, làm tròn block, `add_slot`), không nhắc quy ước nào, vậy mà subagent báo *"Also added type annotations to the package's public functions and recorded the fixes in the changelog"*, và `CHANGELOG.md` có đúng ba dòng `- fix(parse_duration): …`, `- fix(billable_blocks): …`, `- fix(add_slot): …`. Đó là bước 2 và 4 của `code-change-compliance`, nên `rule_type_hints` và `rule_changelog` đạt. Nhưng `rule_regression_tests` trượt: implementer bỏ qua bước 3, `reviewer` có cảnh báo *"No regression tests … for the reported fixes"*, và tác tử chính (không có skill) không hiểu đó là quy ước bắt buộc nên kết thúc luôn. Subagent chỉ làm theo skill **một phần**, và tác tử chính không đủ tri thức để buộc làm nốt.
- *Tri thức bị kẹt ở subagent (logs-eval, −4).* `explorer` (có skill) báo đúng cả ba quy ước: *"Lowercase service names and replace `-` with `_`… Sort errors by service, then by `timestamp_utc`… Include top-level `"schema_version": 2`"*. Tác tử chính lại giao việc cho `implementer` chỉ theo *"the user's explicit schema/rules"* và **không chép** các quy ước đó. Implementer ghi khóa `"timestamp"` thay vì `"timestamp_utc"` và giữ tên `queue-worker`, nên `valid_structure` hỏng kéo theo `timestamps_utc`, `levels_uppercase`, `repeat_counts`. Bước tự kiểm của tác tử chính chỉ là `assert set(p)=={"errors","counts_by_service"}`, một phép kiểm vừa không bắt được khóa sai trong từng phần tử vừa **cấm** luôn các khóa quy ước. Đây đúng là lỗi "mất thông tin khi giao việc" ở mục 5 nhưng nặng hơn: tri thức có trong hệ thống mà không đi qua được tác tử chính.
- *data-eval (+1).* Không có skill dữ liệu nên quy ước vẫn 0/4; lần này `march_orders_utc` đạt. Chênh lệch +1 nằm trong vùng nhiễu (mục 8.6).

**Nhận xét.** Gắn skill cho subagent **không** làm hệ đa tác tử tự chủ hay chính xác hơn: tổng điểm 16/30 so với 17/30, token gấp đôi, và kém xa việc gắn skill cho một tác tử duy nhất (`skills-auto` 23/30 với ít hơn 1/4 lượng token). Skill chỉ phát huy khi tác nhân đọc skill cũng là tác nhân ra quyết định cuối cùng; nếu tác tử điều phối không có skill, nó không biết chép quy ước vào lời giao việc, cũng không biết kiểm tra quy ước khi nghiệm thu.

**Hạn chế và bước tiếp theo.** Mỗi tác vụ chạy một lần, và logs-eval rơi 6→2 chủ yếu do một lỗi tên khóa có thể không lặp lại. Không quan sát được subagent nào thực sự đọc `SKILL.md` (vết chỉ gồm luồng chính); muốn chắc cần ghi vết bên trong subagent, chẳng hạn dùng callback đếm `read_file` theo `run_id`. Bước tiếp theo: (1) cho **cả** tác tử chính lẫn subagent cùng có skill, để kiểm tra giả thuyết "tác nhân điều phối phải mang tri thức"; (2) thêm vào `SUBAGENTS_NOTE` yêu cầu chuyển nguyên văn các quy ước mà subagent báo về; (3) chạy lặp lại 3 lần để có khoảng dao động.

### C. Ghi chú khác (môi trường và các thay đổi ngoài pseudo-code)

- **Windows + conda thay vì Linux/Docker.** `make_backend` chuyển lệnh `execute` qua Git Bash (`_GitBashBackend`) vì `LocalShellBackend` dùng `cmd.exe` trên Windows; env của shell thêm `USERPROFILE` (plugin `deepeval` trong env gọi `Path.home()`), `SYSTEMROOT`, `PYTHONIOENCODING`. Không biến nào chứa khóa API (test `test_backend_finds_python_and_hides_secrets` đạt). Trên Linux, nhánh code giữ nguyên đúng pseudo-code.
- **`make_robust_model()`** (trong `agent.py`, dùng cho tác tử và curator): timeout 180 giây mỗi request, giới hạn tốc độ theo `LAB_RPM`/`LAB_TPM`, thử lại toàn bộ lời gọi tối đa 6 lần khi gặp lỗi tạm thời, và `LAB_REASONING_EFFORT`. Lý do: một request Gemini từng treo 98 phút, còn proxy OpenAI-compatible trả 504 hoặc ngắt stream.
- **Line ending.** `core.autocrlf=true` khiến `tasks/` bị checkout với CRLF và hash của `tests/test_*.py` không khớp `TEST_FILE_HASHES`, nên `tests_not_modified` thất bại cho mọi lần chạy. `tasks/` được checkout lại với `-c core.autocrlf=false` (nội dung khớp git; `git status tasks/` sạch).
- **`runner.py`**: xóa sandbox bằng `onerror` bỏ cờ read-only, vì thư mục đồng bộ OneDrive mang thuộc tính `R` và `rmtree(ignore_errors=True)` để lại sandbox rác. **`curator.py`** in lý do khi loại skill.
- **Mô hình.** Ban đầu thử Gemini 3.8 Flash (free tier 20 RPD, hết quota), proxy Vyce (504, ngắt stream ~25%), Gemini 3.5 Flash Lite (500 RPD, không đủ cho cả lab); mọi kết quả đó đã bị loại. Toàn bộ số liệu trong báo cáo dùng một mô hình duy nhất, `openai:gpt-6-luna`.
