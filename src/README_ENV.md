# 📝 Environment Configuration Guide

## Quick Start

### 1. Tạo file `.env` từ template

```powershell
# PowerShell
cd src
Copy-Item env.example .env
```

```bash
# Bash
cd src
cp env.example .env
```

### 2. Chỉnh sửa `.env` nếu cần

File `.env` sẽ **tự động ghi đè** tất cả default values trong `config_settings.py`.

### 3. Kiểm tra log khi start app

Khi chạy ứng dụng, bạn sẽ thấy:

```
✅ Loaded .env from: D:\GIT\...\src\.env
   ENV_OVERRIDE=true (.env will override system env vars)
```

## ⚙️ Cấu hình Priority

Thứ tự ưu tiên (từ cao đến thấp):

1. **System Environment Variables** (nếu `ENV_OVERRIDE=false`)
2. **`.env` file values** ← **Luôn ghi đè default values**
3. **Default values** trong `config_settings.py`

## 🔧 ENV_OVERRIDE Control

Trong file `.env`, bạn có thể control behavior:

```env
# .env sẽ ghi đè cả system env vars (mặc định)
ENV_OVERRIDE=true

# System env vars sẽ có priority cao hơn .env
ENV_OVERRIDE=false
```

## 📋 Các biến quan trọng

### Database
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/context_handling_db
```

### Redis
```env
REDIS_URL=redis://localhost:6379/0
```

### API Port
```env
API_PORT=30020
```

## 🚨 Lưu ý

- File `.env` đã được ignore trong `.gitignore` - **KHÔNG commit** file này
- Luôn dùng `env.example` làm template
- Thay đổi `SECRET_KEY` trong production!
- File `.env` luôn ghi đè default values (ENV_OVERRIDE=true mặc định)

## 📚 Xem thêm

- `docs/TROUBLESHOOTING_DB_REDIS.md` - Troubleshooting guide
- `app/core/config_settings.py` - Source code của config system


