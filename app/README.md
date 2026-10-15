# EduResult IDOR Lab

Ứng dụng Flask mô phỏng cổng tra cứu điểm thi, dành cho sandbox CyberRangeCZ/MekoDataCTF.

## Chạy trên Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Mặc định ứng dụng lắng nghe cổng `5000`. Truy cập `http://IP_MAY_CHU:5000/`. Chỉ mở trong mạng sandbox cô lập; không đưa lab dễ tổn thương lên Internet.

## Tài khoản demo
- `alice` / `AliceLab123!` — SV2024001
- `bob` / `BobLab123!` — SV2024002
- `chi` / `ChiLab123!` — SV2024003

## API
- `POST /api/login` — JSON `{ "username": "alice", "password": "AliceLab123!" }`
- `POST /api/logout`
- `GET /api/me`
- `GET /api/exams` — chỉ liệt kê kết quả của tài khoản hiện tại
- `GET /api/exams/<id>` — cố ý thiếu kiểm tra quyền sở hữu (IDOR)
- `PATCH /api/exams/<id>` — cố ý thiếu kiểm tra quyền sở hữu khi cập nhật trạng thái
- `GET /api/health`

## Kiểm thử IDOR
1. Đăng nhập bằng `alice`.
2. Mở kết quả `1001` trong giao diện.
3. Trong DevTools Console, chạy `fetch('/api/exams/1002').then(r=>r.json()).then(console.log)`. Kết quả của Bob sẽ được trả về do lỗi IDOR cố ý.
4. Thử cập nhật trạng thái `1002` bằng PATCH, rồi đăng nhập Bob để xác nhận.
5. Để vá lỗi, trong cả hai route chi tiết và cập nhật của `app.py`, thêm:
   `if exam["owner"] != session["username"]: return jsonify(error="Không có quyền truy cập"), 403`

Dữ liệu nằm trong bộ nhớ, restart app sẽ reset các thay đổi. Đây là mã lab cố ý dễ tổn thương; không dùng dữ liệu hoặc mật khẩu thật. Đổi `app.secret_key` trước khi sử dụng.
