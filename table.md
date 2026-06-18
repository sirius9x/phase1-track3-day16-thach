# Phân tích Chi phí và Token (Cost & Token Analysis)

Bảng dưới đây tính toán ước lượng chi phí sử dụng API của model `gemini-2.5-flash-lite` cho bài Lab Reflexion dựa trên tập dữ liệu 100 câu hỏi (`hotpot_test.json`).

## 1. Bảng giá Model Gemini 2.5 Flash Lite
*(Bảng giá tham khảo từ Google AI Studio cho bản Flash-Lite)*
- **Input Tokens (Prompt):** ~$0.075 / 1 Triệu tokens
- **Output Tokens (Completion):** ~$0.30 / 1 Triệu tokens

## 2. Phân bổ Token cho 1 Lượt chạy (Ước tính)

| Thành phần Gọi LLM | Input Tokens (ước tính) | Output Tokens (ước tính) | Ghi chú |
|:---|:---:|:---:|:---|
| **Actor (Lượt 1)** | ~400 | ~50 | Đọc System Prompt + Question + Context + Trả lời. |
| **Evaluator** | ~200 | ~50 | Chấm điểm dựa trên Gold Answer và xuất ra JSON. |
| **Reflector (Nếu sai)** | ~500 | ~100 | Phân tích nguyên nhân sai + xuất chiến lược JSON. |
| **Actor (Lượt > 1)** | ~600 | ~50 | Phải gánh thêm lịch sử `reflection_memory` ngày càng dài. |

## 3. Tổng chi phí cho Tập Benchmark (100 Câu hỏi)

| Agent | Kịch bản / Số lượt thử | Tổng Input | Tổng Output | Chi phí Input ($) | Chi phí Output ($) | **Tổng Chi Phí ($)** |
|:---|:---|---:|---:|---:|---:|---:|
| **ReAct Agent** | Luôn chạy 1 lượt | 60,000 | 10,000 | $0.0045 | $0.0030 | **$0.0075** |
| **Reflexion Agent**| Lý tưởng (Đúng ngay lượt 1) | 60,000 | 10,000 | $0.0045 | $0.0030 | **$0.0075** |
| **Reflexion Agent**| Tệ nhất (Thử 3 lượt mới xong/bỏ cuộc) | ~250,000 | ~40,000 | $0.0187 | $0.0120 | **$0.0307** |
| **Reflexion Agent**| Thực tế (Trung bình ~2 lượt/câu) | 150,000 | 25,000 | $0.0112 | $0.0075 | **$0.0187** |

> **💡 Nhận xét:** 
> - Chi phí chạy bài Lab trên 100 câu bằng model `gemini-2.5-flash-lite` là cực kỳ rẻ, **chưa tới $0.02 (khoảng 500 VNĐ)** cho toàn bộ Benchmark. 
> - Đánh đổi của kiến trúc Reflexion: Độ trễ (Latency) và Chi phí (Cost) sẽ cao gấp 2-3 lần so với ReAct tiêu chuẩn. Điều này là do hệ thống phải liên tục "nhồi" thêm bài học (`reflection_memory`) vào Input Prompt và phải gọi thêm các Agent phụ (Reflector).

## 4. Công thức tự tính toán sau khi có Report
Sau khi tiến trình `run_benchmark.py` chạy xong, bạn mở file `outputs/real_run/report.json` và xem phần `summary`. 
Dựa vào chỉ số `avg_token_estimate` hệ thống đếm được (Token đếm từ Usage Metadata của Gemini rất chuẩn xác), bạn có thể tính tiền thực tế:

```text
Tổng Tokens của Agent = avg_token_estimate * num_records
Tổng tiền ($) = (Tổng Tokens / 1,000,000) * 0.15$ (Tính giá trung bình gom chung Input/Output)
```
