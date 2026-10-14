# Guestbook: Manual và Vibe Code

Ứng dụng Flask theo yêu cầu bài tập hai buổi. Cả hai phiên bản có route danh sách, form thêm, xóa theo ID, lưu JSON và trang thống kê có biểu đồ Matplotlib. Dữ liệu được giữ trong list Python khi ứng dụng chạy và ghi lại vào `data.json` sau thao tác thêm/xóa.

## Hai phiên bản

- `manual/`: cách tổ chức nhiều tệp Flask. Frontend dùng HTML cơ bản trong `templates/`, xử lý route trong `app.py`.
- `vibe-code/`: bản một tệp Python, HTML/CSS nằm trong chuỗi template để dễ xem một ví dụ gọn.

Mỗi thư mục có file JSON riêng, được tạo tự động sau khi thêm/xóa lời nhắn. File JSON và biểu đồ PNG là dữ liệu sinh ra tại máy và được Git bỏ qua.

## Chức năng

- `GET /`: hiển thị danh sách từ biến list toàn cục `entries`.
- `GET /add`: hiển thị form hai trường `name`, `message`.
- `POST /add`: kiểm tra hai trường không trống; nếu hợp lệ thì thêm entry, lưu JSON và chuyển về `/`; nếu không hợp lệ thì render lại form cùng thông báo.
- `POST /delete/<id>`: xóa entry theo ID, lưu JSON và chuyển về `/`.
- `GET /stats`: hiển thị tổng số lời nhắn, top 5 người gửi và biểu đồ cột theo người gửi. Biểu đồ được tạo bằng Matplotlib vào `static/stats.png`.

## Chạy phiên bản Manual

```powershell
cd manual
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Mở http://127.0.0.1:5000. Dừng server bằng `Ctrl+C`.

## Chạy phiên bản Vibe Code

Mở cửa sổ terminal khác hoặc dừng server bản Manual, rồi:

```powershell
cd vibe-code
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

## Upload thay đổi lên GitHub

Nếu repository đã được kết nối, mở PowerShell tại thư mục gốc `guestbook` và chạy:

```powershell
git add .
git commit -m "Update guestbook to match class requirements"
git push
```

Lần đầu upload, tạo repository trống trên GitHub, rồi kết nối bằng `git remote add origin https://github.com/USERNAME/guestbook.git` và `git push -u origin main`.
