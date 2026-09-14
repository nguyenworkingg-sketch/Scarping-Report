# Scarping-Report

Tự động đăng nhập HSC + Vietcap, tải báo cáo research về máy Windows và xóa dữ liệu quá 30 ngày.

## 1. Clone repo về máy

```powershell
cd E:\
git clone https://github.com/nguyenworkingg-sketch/Scarping-Report.git
cd Scarping-Report
```

## 2. Cài đặt lần đầu

Double-click `setup_windows.bat`.

Script sẽ:
- tạo `.venv`
- cài Python packages
- cài Chromium cho Playwright
- tạo `.env` từ `.env.example`

## 3. CHỖ ĐIỀN TÀI KHOẢN

Mở file `.env` nằm ngay trong thư mục repo và sửa 4 dòng này:

```env
HSC_EMAIL=TEN_DANG_NHAP_HSC_CUA_BAN
HSC_PASSWORD=MAT_KHAU_HSC_CUA_BAN

VIETCAP_USERNAME=TEN_DANG_NHAP_VIETCAP_CUA_BAN
VIETCAP_PASSWORD=MAT_KHAU_VIETCAP_CUA_BAN
```

Giữ nguyên nếu muốn lưu vào ổ E:

```env
REPORT_ROOT=E:\Báo cáo
RETENTION_DAYS=30
HEADLESS=true
MAX_REPORTS=30
```

**Không commit file `.env` lên GitHub.** Repo đã có `.gitignore` để chặn `.env` và session login.

## 4. Chạy thử

Chạy cả hai nguồn:

```powershell
.\.venv\Scripts\python.exe main.py --source all
```

Chỉ HSC:

```powershell
.\.venv\Scripts\python.exe main.py --source hsc
```

Chỉ Vietcap:

```powershell
.\.venv\Scripts\python.exe main.py --source vietcap
```

Hoặc double-click `run_scraper.bat`.

## 5. Nếu HSC/Vietcap yêu cầu OTP hoặc CAPTCHA

Không bypass CAPTCHA. Tạo session thủ công:

```powershell
.\.venv\Scripts\python.exe bootstrap_auth.py hsc
```

hoặc:

```powershell
.\.venv\Scripts\python.exe bootstrap_auth.py vietcap
```

Trình duyệt sẽ mở. Đăng nhập bình thường, nhập OTP/CAPTCHA nếu có, sau đó quay lại terminal và nhấn Enter. Session sẽ lưu trong `auth/` trên máy và không được commit lên GitHub.

## 6. Dữ liệu lưu ở đâu?

Mặc định:

```text
E:\Báo cáo\
├── raw\
│   ├── hsc\
│   └── vietcap\
├── extracted\
│   ├── hsc\
│   └── vietcap\
└── metadata\
    ├── hsc\
    └── vietcap\
```

- `raw`: PDF gốc
- `extracted`: text đã trích từ PDF để AI/search xử lý nhanh
- `metadata`: URL nguồn, thời điểm tải, SHA-256 và đường dẫn file

## 7. Tự xóa dữ liệu quá 30 ngày

Mỗi lần `main.py` chạy, chương trình tự xóa file trong `raw`, `extracted`, `metadata` có thời gian sửa đổi quá `RETENTION_DAYS`.

Mặc định:

```env
RETENTION_DAYS=30
```

Muốn giữ 60 ngày thì đổi thành `60`.

## 8. Chạy tự động trên Windows

Mở PowerShell **Run as Administrator**, vào thư mục repo và chạy:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_task.ps1 -Time 07:20
```

Task Scheduler sẽ chạy scraper mỗi ngày lúc 07:20.

Đổi sang 12:30:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_task.ps1 -Time 12:30
```

Nếu muốn nhiều khung giờ, có thể tạo thêm task với tên khác:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_task.ps1 -TaskName BrokerResearchMorning -Time 07:20
powershell -ExecutionPolicy Bypass -File .\setup_task.ps1 -TaskName BrokerResearchNoon -Time 12:20
```

## GitHub Actions và ổ E:\

GitHub-hosted Actions chạy trên máy chủ GitHub nên **không thể ghi trực tiếp vào ổ E: trên máy cá nhân của bạn**.

Để dữ liệu luôn nằm offline tại `E:\Báo cáo`, dùng Windows Task Scheduler như trên. Nếu sau này muốn bấm/chạy workflow từ GitHub nhưng vẫn tải vào ổ E:, cần cài **GitHub self-hosted runner** trên chính máy Windows này.

## Lưu ý

Scraper chỉ sử dụng tài khoản hợp lệ của bạn và nội dung tài khoản đó được phép truy cập. Nó không bypass CAPTCHA, paywall hay quyền truy cập.

Do DOM sau đăng nhập của HSC/Vietcap có thể thay đổi, lần chạy đầu tiên có thể cần chỉnh selector hoặc đường dẫn report list dựa trên log thực tế.
