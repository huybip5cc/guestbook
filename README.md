# Guestbook: Manual và Vibe Code

Ứng dụng guestbook nhỏ dùng Python, Flask và SQLite. Có thể xem lời nhắn, gửi lời nhắn mới và xóa lời nhắn theo ID.

## Hai phiên bản

- `manual/`: tổ chức theo cấu trúc Flask quen thuộc, giao diện ở `templates/`, CSS ở `static/`, xử lý và lưu DB ở `app.py`.
- `vibe-code/`: bản mẫu đơn tệp, phù hợp để thử nghiệm nhanh hoặc dùng làm đầu vào cho AI coding. Chức năng và dữ liệu SQLite tương đương.

Mỗi phiên bản chạy độc lập và tạo database riêng trong thư mục của phiên bản đó.

## Chạy phiên bản Manual

```bash
cd manual
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Mở http://127.0.0.1:5000.

## Chạy phiên bản Vibe Code

Làm tương tự trong `vibe-code/`:

```bash
cd vibe-code
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Đưa dự án lên GitHub

1. Đăng nhập [GitHub](https://github.com), chọn **New repository**, đặt tên ví dụ `guestbook`, để repository trống (không chọn tạo README vì dự án đã có README).
2. Cài Git nếu máy chưa có, rồi mở Terminal/PowerShell tại thư mục `guestbook` đã tải hoặc giải nén.
3. Chạy các lệnh sau (thay `YOUR_USERNAME` bằng tên tài khoản GitHub và chỉnh URL repository nếu đặt tên khác):

```bash
git init
git add .
git commit -m "Build guestbook app with manual and vibe-code versions"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/guestbook.git
git push -u origin main
```

Nếu Git yêu cầu đăng nhập, hoàn tất xác thực trong cửa sổ trình duyệt hoặc dùng GitHub CLI (`gh auth login`). Không đưa mật khẩu/token vào mã nguồn.

## Chức năng và lưu ý

- Tên và nội dung bắt buộc; nội dung tối đa 1000 ký tự.
- Lời nhắn được lưu bền vững bằng SQLite. Xóa dùng HTTP POST và CSRF token phiên.
- Demo chỉ chạy trên máy cá nhân (`127.0.0.1`). Muốn triển khai công khai cần cấu hình máy chủ WSGI, `SECRET_KEY` bí mật, HTTPS, và bảo vệ xóa phù hợp; không dùng Flask development server cho production.
