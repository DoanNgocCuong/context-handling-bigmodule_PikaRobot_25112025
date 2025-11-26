# 🔧 Troubleshooting: Database và Redis Connection Issues

## 📋 Vấn đề

Khi chạy ứng dụng bằng `uvicorn`, gặp lỗi:
- **PostgreSQL**: `Connection refused` tại `localhost:5432`
- **Redis**: `Timeout connecting to server` tại `localhost:6379`

## 🔍 Nguyên nhân

### 1. **Docker Services chưa được start**
- Code đang cố kết nối tới `localhost:5432` (PostgreSQL) và `localhost:6379` (Redis)
- Nhưng các Docker containers chưa được khởi động
- Kết quả: Connection refused / Timeout

### 2. **Thiếu file `.env` hoặc `.env` không được load đúng**
- Không có file `.env` trong thư mục `src/`
- Code đang dùng default values từ `config_settings.py`
- Default values đúng nhưng services chưa chạy
- **Lưu ý**: Code đã được cấu hình để `.env` luôn ghi đè default values (ENV_OVERRIDE=true mặc định)

### 3. **Chạy ngoài Docker network**
- Uvicorn chạy trực tiếp trên host (không qua Docker)
- Cần kết nối tới services đang chạy trên localhost ports

## ✅ Giải pháp

### **Giải pháp 1: Start Docker Services (Khuyến nghị)**

#### Bước 1: Start chỉ PostgreSQL và Redis (không start API service)

```bash
cd src
docker-compose up -d postgres redis
```

#### Bước 2: Kiểm tra services đã chạy

```bash
docker ps
```

Bạn sẽ thấy:
- `context_handling_postgres` - Running on port 5432
- `context_handling_redis` - Running on port 6379

#### Bước 3: Chạy ứng dụng

```bash
cd src
uvicorn app.main_app:app --reload --host 0.0.0.0 --port 30020
```

#### Bước 4: Test health check

```bash
curl http://localhost:30020/v1/health
```

---

### **Giải pháp 2: Tạo file `.env` để ghi đè config (Khuyến nghị)**

#### Bước 1: Copy file example

```bash
cd src
copy env.example .env
```

Hoặc trên PowerShell:
```powershell
cd src
Copy-Item env.example .env
```

#### Bước 2: Kiểm tra và chỉnh sửa `.env` nếu cần

File `.env` sẽ có các giá trị mặc định:
```env
ENV_OVERRIDE=true
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/context_handling_db
REDIS_URL=redis://localhost:6379/0
API_PORT=30020
# ... và các config khác
```

**Lưu ý quan trọng:**
- `ENV_OVERRIDE=true` (mặc định): `.env` sẽ **ghi đè** cả system environment variables
- `ENV_OVERRIDE=false`: System env vars sẽ có priority cao hơn `.env`
- File `.env` luôn ghi đè default values trong `config_settings.py`

#### Bước 3: Đảm bảo Docker services đang chạy

```bash
docker-compose up -d postgres redis
```

#### Bước 4: Chạy ứng dụng và kiểm tra log

Khi start app, bạn sẽ thấy log:
```
✅ Loaded .env from: D:\GIT\...\src\.env
   ENV_OVERRIDE=true (.env will override system env vars)
```

Nếu không có file `.env`, sẽ có warning:
```
⚠️  .env file not found at: D:\GIT\...\src\.env
   Using default values from config_settings.py
   💡 Create ...\.env to override default values
```

---

### **Giải pháp 3: Start tất cả services (Nếu muốn chạy full stack trong Docker)**

```bash
cd src
docker-compose up -d
```

Lưu ý: Nếu chạy API trong Docker, bạn sẽ không cần chạy `uvicorn` riêng nữa.

---

## 🧪 Kiểm tra kết nối

### Test PostgreSQL connection:

```bash
# Kiểm tra container đang chạy
docker ps | findstr postgres

# Test connection từ host
psql -h localhost -p 5432 -U postgres -d context_handling_db
# Password: postgres
```

### Test Redis connection:

```bash
# Kiểm tra container đang chạy
docker ps | findstr redis

# Test connection từ host
redis-cli -h localhost -p 6379 ping
# Kết quả mong đợi: PONG
```

---

## 📝 Lưu ý

1. **Port conflicts**: Nếu port 5432 hoặc 6379 đã được sử dụng bởi service khác, bạn cần:
   - Stop service đó, hoặc
   - Thay đổi port mapping trong `docker-compose.yml`

2. **Docker Desktop**: Đảm bảo Docker Desktop đang chạy trên Windows

3. **Network**: Khi chạy `uvicorn` trực tiếp (không qua Docker), phải dùng `localhost` thay vì tên service (`postgres`, `redis`)

4. **Health check**: Sau khi start services, đợi vài giây để health checks pass trước khi chạy app

---

## 🚀 Quick Start Commands

```bash
# 1. Start services
cd src
docker-compose up -d postgres redis

# 2. Đợi 5-10 giây để services ready

# 3. Chạy app
uvicorn app.main_app:app --reload --host 0.0.0.0 --port 30020

# 4. Test
curl http://localhost:30020/v1/health
```

---

## ❓ FAQ

**Q: Tại sao không dùng `docker-compose up` để start tất cả?**  
A: Vì bạn đang chạy `uvicorn` trực tiếp trên host, chỉ cần start DB và Redis. Nếu start cả API service trong Docker, sẽ conflict port.

**Q: Có cần file `.env` không?**  
A: **Khuyến nghị có** để:
- Dễ dàng customize config mà không cần sửa code
- `.env` luôn ghi đè default values (ENV_OVERRIDE=true mặc định)
- Tách biệt config giữa các môi trường (dev/staging/prod)
- File `.env` đã được ignore trong `.gitignore`, an toàn cho secrets

**Q: Làm sao để `.env` KHÔNG ghi đè system environment variables?**  
A: Đặt `ENV_OVERRIDE=false` trong file `.env` hoặc set biến môi trường `ENV_OVERRIDE=false` trước khi chạy app.

**Q: Làm sao biết services đã sẵn sàng?**  
A: Chạy `docker ps` và kiểm tra status là "Up" và health check pass. Hoặc test bằng `psql` / `redis-cli`.

