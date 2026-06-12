# 新竹團購平台 — 快速啟動

## 環境需求
- Docker Desktop（含 Compose）
- Node 20+（前端本地開發）
- Python 3.12+（後端本地開發）

---

## 1. 環境設定

```bash
cp .env.example backend/.env
# 編輯 backend/.env，至少確認 SMS_PROVIDER=mock（開發不需要真實簡訊）
```

---

## 2. 啟動基礎服務（PostgreSQL + Redis）

```bash
docker compose up -d postgres redis
```

---

## 3. 資料庫初始化

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head          # 建立所有資料表
python seed.py                # 植入測試資料
```

---

## 4. 啟動後端

```bash
uvicorn app.main:app --reload --port 8000
```

API 文件：http://localhost:8000/docs

---

## 5. 啟動前端（三個 SPA）

各開一個終端：

```bash
# 消費者端
cd frontend-consumer && npm install && npm run dev   # http://localhost:5173

# 商家端
cd frontend-merchant && npm install && npm run dev   # http://localhost:5174

# 管理後台
cd frontend-admin && npm install && npm run dev      # http://localhost:5175
```

---

## 6. 測試帳號

| 角色 | 帳號 | 密碼 |
|------|------|------|
| 消費者 | user@test.com | test1234 |
| 商家（肉乾王） | meat@test.com | test1234 |
| 商家（米粉嫂） | noodle@test.com | test1234 |
| 商家（下午茶） | tea@test.com | test1234 |
| 平台管理員 | admin@test.com | admin1234 |

---

## 7. 全部用 Docker（一鍵啟動）

```bash
docker compose up --build
```

啟動後執行 seed（一次性）：

```bash
docker compose exec backend python seed.py
```

---

## 主要端點

| 服務 | URL |
|------|-----|
| 後端 API | http://localhost:8000/api/v1 |
| Swagger 文件 | http://localhost:8000/docs |
| 消費者 App | http://localhost:5173 |
| 商家後台 | http://localhost:5174 |
| 管理後台 | http://localhost:5175 |
| WebSocket | ws://localhost:8000/ws/merchant/{id} |
