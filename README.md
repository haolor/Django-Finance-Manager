# Django Finance Manager

He thong quan ly tai chinh ca nhan su dung Django REST API + React (Vite), ho tro:

- Quan ly giao dich thu/chi theo danh muc
- Dat ngan sach va canh bao vuot ngan sach
- Thong ke, bao cao, dashboard
- NLP input (nhap giao dich bang ngon ngu tu nhien)
- OCR hoa don (trich xuat giao dich tu anh)
- AI insights (trend, prediction, anomaly, savings)
- Chatbot ho tro tai chinh
- API sync cho mobile

## 1) Cong nghe su dung

- Backend: Django 6, Django REST Framework, Token Authentication
- Frontend: React 18, Vite, TailwindCSS
- Database: PostgreSQL
- AI/OCR: Gemini API, EasyOCR, Pillow

## 2) Yeu cau he thong

- Python 3.11+ (khuyen nghi 3.11 hoac 3.12)
- Node.js 18+ va npm
- PostgreSQL 14+
- Git

## 3) Cai dat day du

### Buoc 1: Clone source

```bash
git clone <your-repo-url>
cd Django-Finance-Manager
```

### Buoc 2: Tao virtual environment va cai dependencies backend

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Buoc 3: Tao database PostgreSQL

Tao database (vi du):

```sql
CREATE DATABASE finance_db;
```

Mac dinh project dang dung:

- DB Name: `finance_db`
- DB User: `postgres`
- DB Host: `127.0.0.1`
- DB Port: `5432`

Ban nen cau hinh lai thong tin nay bang bien moi truong (xem muc `.env.local` ben duoi).

### Buoc 4: Tao file moi truong `.env.local`

Tao file `.env.local` o thu muc goc project voi noi dung mau:

```env
# Django
DEBUG=True
SECRET_KEY=replace-with-your-secret-key

# Database
DB_NAME=finance_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Email (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=Finance Manager <noreply@financemanager.com>

# Gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3-flash-preview
```

Luu y quan trong:

- Khong commit `.env.local` len git.
- Nen xoa/doi tat ca secrets hard-code neu dang deploy production.

### Buoc 5: Migrate va tao du lieu mau

```bash
python manage.py migrate
python manage.py init_categories
```

Neu muon tao tai khoan admin:

```bash
python manage.py createsuperuser
```

### Buoc 6: Cai dat frontend

```bash
cd frontend
npm install
```

### Buoc 7: Chay ung dung o che do phat trien

Mo 2 terminal:

Terminal 1 (backend):

```bash
python manage.py runserver 0.0.0.0:8000
```

Terminal 2 (frontend):

```bash
cd frontend
npm run dev
```

Truy cap:

- Frontend dev: `http://localhost:5173`
- API backend: `http://localhost:8000/api/`

### Buoc 8: Build frontend de Django serve

```bash
cd frontend
npm run build
```

Sau khi build, Django se serve frontend tu `static/frontend`.

## 4) Cau truc thu muc

```text
Django-Finance-Manager/
|-- manage.py
|-- requirements.txt
|-- README.md
|-- mysite/                      # Cau hinh project Django
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
|-- finance/                     # App chinh backend
|   |-- models.py                # Category, Transaction, Budget, ...
|   |-- serializers.py
|   |-- views.py                 # REST APIs + custom actions
|   |-- urls.py
|   |-- ai_service.py
|   |-- gemini_service.py
|   |-- nlp_service.py
|   |-- ocr_service.py
|   |-- notification_service.py
|   `-- management/commands/
|       `-- init_categories.py
|-- frontend/                    # React + Vite app
|   |-- package.json
|   |-- vite.config.js
|   `-- src/
|       |-- pages/
|       |-- components/
|       |-- contexts/
|       `-- services/api.js
|-- static/frontend/             # Frontend da build de Django phuc vu
|-- MOBILE_API.md                # Tai lieu mobile sync API
|-- EMAIL_SETUP_GUIDE.md
`-- ...
```

## 5) Authentication

He thong dung Token Authentication (DRF Token).

1. Dang ky hoac dang nhap de lay token
2. Gui token qua header:

```http
Authorization: Token <your_token>
```

Tat ca endpoint (tru auth/register, auth/login, api root) deu yeu cau token.

## 6) Danh sach API Endpoints

Base URL:

```text
http://localhost:8000/api/
```

### 6.1 Public endpoints

- `GET /api/` - API root
- `POST /api/auth/register/` - Dang ky tai khoan
- `POST /api/auth/login/` - Dang nhap, tra ve token

### 6.2 Auth & Preferences (can token)

- `GET /api/auth/profile/` - Lay thong tin user hien tai
- `GET /api/auth/preferences/` - Lay user preferences
- `PUT /api/auth/preferences/` - Cap nhat toan bo preferences
- `PATCH /api/auth/preferences/` - Cap nhat mot phan preferences

### 6.3 Categories (can token)

- `GET /api/categories/` - Danh sach danh muc
- `POST /api/categories/` - Tao danh muc
- `GET /api/categories/{id}/` - Chi tiet danh muc
- `PUT /api/categories/{id}/` - Sua danh muc
- `PATCH /api/categories/{id}/` - Sua mot phan danh muc
- `DELETE /api/categories/{id}/` - Xoa danh muc

### 6.4 Transactions (can token)

CRUD co ban:

- `GET /api/transactions/` - Danh sach giao dich (ho tro query: `category`, `start_date`, `end_date`)
- `POST /api/transactions/` - Tao giao dich
- `GET /api/transactions/{id}/` - Chi tiet giao dich
- `PUT /api/transactions/{id}/` - Sua giao dich
- `PATCH /api/transactions/{id}/` - Sua mot phan
- `DELETE /api/transactions/{id}/` - Xoa giao dich

Custom actions:

- `GET /api/transactions/statistics/` - Thong ke thu/chi (`period=all` hoac `start_date`, `end_date`)
- `GET /api/transactions/expenses/` - Lay toan bo giao dich chi tieu
- `POST /api/transactions/nlp_input/` - Tao giao dich tu cau mo ta tu nhien
- `POST /api/transactions/ocr_receipt/` - Upload anh hoa don, OCR + tao giao dich
- `GET /api/transactions/sync/` - Dong bo transactions cho mobile
- `POST /api/transactions/bulk_sync/` - Dong bo tao/sua/xoa hang loat tu mobile
- `POST /api/transactions/nlp_query/` - Truy van giao dich bang ngon ngu tu nhien

### 6.5 Budgets (can token)

- `GET /api/budgets/` - Danh sach ngan sach
- `POST /api/budgets/` - Tao ngan sach
- `GET /api/budgets/{id}/` - Chi tiet ngan sach
- `PUT /api/budgets/{id}/` - Sua ngan sach
- `PATCH /api/budgets/{id}/` - Sua mot phan ngan sach
- `DELETE /api/budgets/{id}/` - Xoa ngan sach
- `GET /api/budgets/sync/` - Dong bo budgets cho mobile

### 6.6 Notifications (can token)

- `GET /api/notifications/` - Danh sach thong bao
- `POST /api/notifications/` - Tao thong bao
- `GET /api/notifications/{id}/` - Chi tiet thong bao
- `PUT /api/notifications/{id}/` - Sua thong bao
- `PATCH /api/notifications/{id}/` - Sua mot phan thong bao
- `DELETE /api/notifications/{id}/` - Xoa thong bao
- `POST /api/notifications/{id}/mark_read/` - Danh dau da doc
- `POST /api/notifications/mark_all_read/` - Danh dau tat ca da doc
- `GET /api/notifications/unread_count/` - Lay so thong bao chua doc

### 6.7 AI & Reports (can token)

- `POST /api/reports/custom/` - Tao bao cao tuy chinh theo preferences
- `GET /api/ai/trends/` - Phan tich xu huong chi tieu
- `GET /api/ai/predictions/` - Du doan chi tieu thang tiep theo
- `GET /api/ai/anomalies/` - Phat hien giao dich bat thuong
- `GET /api/ai/savings-suggestions/` - Goi y tiet kiem
- `POST /api/chatbot/` - Chatbot ho tro tai chinh (Gemini/fallback)

### 6.8 Mobile sync endpoint tong hop (can token)

- `GET /api/sync/all/` - Dong bo transactions + budgets + categories trong 1 request

Chi tiet them ve mobile dong bo xem file `MOBILE_API.md`.

## 7) Vi du request nhanh

Dang nhap:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
	-H "Content-Type: application/json" \
	-d '{"username":"demo_user","password":"demo123"}'
```

Tao giao dich:

```bash
curl -X POST http://localhost:8000/api/transactions/ \
	-H "Authorization: Token <your_token>" \
	-H "Content-Type: application/json" \
	-d '{"category":1,"amount":"50000","description":"An trua","transaction_date":"2026-04-06"}'
```

## 8) FAQ

### 1. Loi khong ket noi duoc PostgreSQL?

- Kiem tra PostgreSQL service da chay chua.
- Kiem tra lai `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.
- Dam bao da tao database `finance_db` (hoac DB ban da config).

### 2. Loi 401 Unauthorized khi goi API?

- Ban chua gui header `Authorization: Token <token>`.
- Token het hieu luc/khong dung user hien tai, hay dang nhap lai.

### 3. Frontend khong hien thi khi mo `http://localhost:8000`?

- Chua build frontend: chay `cd frontend && npm run build`.
- Hoac dang dung dev mode thi truy cap `http://localhost:5173`.

### 4. OCR khong nhan dien duoc hoa don?

- Dung anh ro net, du sang, khong bi mo.
- Dinh dang anh ho tro: JPG, PNG, WebP.
- Kich thuoc toi da 10MB.

### 5. AI (Gemini) khong tra ket qua?

- Kiem tra `GEMINI_API_KEY` trong `.env.local`.
- Kiem tra internet va quota API.
- He thong co fallback local cho mot so API, nhung chat/prediction co the giam chat luong neu Gemini loi.

### 6. Email thong bao khong gui duoc?

- Kiem tra `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, SMTP config.
- Neu dung Gmail, hay dung App Password thay vi mat khau thuong.

### 7. Co the dung SQLite de test nhanh khong?

- Co, nhung project hien tai cau hinh PostgreSQL mac dinh.
- Neu muon chuyen SQLite, can sua `DATABASES` trong settings.

## 9) Tai lieu bo sung

- `MOBILE_API.md` - Tai lieu sync cho mobile
- `MOBILE_SETUP.md` - Huong dan setup mobile
- `EMAIL_SETUP_GUIDE.md` - Huong dan cau hinh email
- `FIX_NOTIFICATION.md`, `FIX_REGISTER_GUIDE.md`, `REGISTER_DEBUG.md` - Tai lieu debug/sua loi