# Web Game Platform - Game TopUp System

Hệ thống nạp tiền game với thanh toán crypto (USDT TRC20) được xây dựng bằng Django và Docker.

## Tính Năng

- Xác thực người dùng với JWT
- Quản lý ví điện tử (deposit, withdrawal)
- Hệ thống đặt hàng nạp game
- Thanh toán qua USDT TRC20 (Tron network)
- Admin dashboard với Jazzmin UI
- API RESTful với Django REST Framework
- Background tasks với Celery
- Multi-language support (EN, VI, CN)
- Rate limiting và security features

## Tech Stack

### Backend
- **Django 5.0** - Web framework
- **Django REST Framework** - API
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **Redis** - Caching & Celery broker
- **Celery** - Background tasks
- **JWT** - Authentication

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy
- **Gunicorn** - WSGI server

### Libraries
- **web3** & **tronpy** - Crypto wallet integration
- **Pillow** - Image processing
- **drf-spectacular** - API documentation
- **Whitenoise** - Static files serving

## Cấu Trúc Dự Án

```
WEBGAME/
├── backend/              # Django backend
│   ├── apps/            # Django apps
│   │   ├── core/       # Core functionality
│   │   ├── users/      # User management
│   │   ├── games/      # Game management
│   │   ├── orders/     # Order processing
│   │   └── wallets/    # Wallet management
│   ├── config/         # Django settings
│   ├── media/          # User uploads
│   └── staticfiles/    # Static files
├── frontend/           # Frontend static files
│   ├── static/        # CSS, JS, images
│   └── templates/     # HTML templates
├── nginx/             # Nginx configuration
├── docker-compose.yml          # Development compose
├── docker-compose.prod.yml     # Production compose
├── Dockerfile                  # Docker image
├── .env.example               # Development env example
├── .env.production.example    # Production env example
└── DEPLOY.md                  # Deployment guide
```

## Quick Start - Development

### 1. Clone Repository

```bash
git clone YOUR_REPOSITORY_URL
cd WEBGAME
```

### 2. Cấu Hình Environment

```bash
cp .env.example .env
# Chỉnh sửa .env với thông tin của bạn
```

### 3. Chạy với Docker (Khuyên dùng)

```bash
# Build và start containers
docker-compose up -d

# Chạy migrations
docker-compose exec backend python manage.py migrate

# Tạo superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

### 4. Chạy Local (Không dùng Docker)

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Truy Cập Application

- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs
- **Frontend**: http://localhost:80 (khi chạy với Nginx)

## Production Deployment

Xem hướng dẫn chi tiết tại [DEPLOY.md](DEPLOY.md)

### Tóm Tắt:

1. Cài đặt Docker trên VPS Ubuntu
2. Clone/upload code lên server
3. Cấu hình `.env` cho production
4. Chạy `docker-compose -f docker-compose.prod.yml up -d`
5. Cấu hình SSL với Let's Encrypt
6. Setup firewall và monitoring

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Users
- `GET /api/users/me/` - Get current user info
- `PUT /api/users/me/` - Update user info

### Games
- `GET /api/games/` - List all games
- `GET /api/games/{id}/` - Game detail
- `GET /api/games/{id}/packages/` - Game packages

### Orders
- `POST /api/orders/` - Create order
- `GET /api/orders/` - List user orders
- `GET /api/orders/{id}/` - Order detail

### Wallets
- `GET /api/wallets/balance/` - Get wallet balance
- `POST /api/wallets/deposit/` - Create deposit
- `POST /api/wallets/withdraw/` - Request withdrawal
- `GET /api/wallets/transactions/` - Transaction history

## Environment Variables

Xem file `.env.example` và `.env.production.example` để biết tất cả các biến môi trường cần thiết.

### Các Biến Quan Trọng:

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `DATABASE_URL` - PostgreSQL connection string
- `ADMIN_USDT_TRC20_ADDRESS` - Wallet address nhận thanh toán
- `TRON_API_KEY` - TronGrid API key

## Development

### Running Tests

```bash
docker-compose exec backend python manage.py test
```

### Making Migrations

```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### Celery Tasks

```bash
# View celery logs
docker-compose logs -f celery

# Monitor celery beat
docker-compose logs -f celery-beat
```

## Security

- JWT authentication cho API
- Rate limiting để chống spam
- CORS configuration
- XSS và CSRF protection
- Secure headers trong production
- HTTPS enforced trong production

## Maintenance

### Backup Database

```bash
docker-compose exec db pg_dump -U gameuser gamedb > backup.sql
```

### View Logs

```bash
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f nginx
```

### Update Dependencies

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Rebuild containers
docker-compose build --no-cache
```

## Troubleshooting

### Database Issues
- Kiểm tra PostgreSQL đang chạy: `docker-compose ps db`
- Reset database: `docker-compose down -v && docker-compose up -d`

### Static Files Not Loading
- Run collectstatic: `docker-compose exec backend python manage.py collectstatic --noinput`
- Restart nginx: `docker-compose restart nginx`

### Celery Not Working
- Check Redis: `docker-compose exec redis redis-cli ping`
- Restart celery: `docker-compose restart celery celery-beat`

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is proprietary software.

## Support

Nếu gặp vấn đề, vui lòng tạo issue hoặc liên hệ team.

---

**Note**: Đảm bảo đọc kỹ [DEPLOY.md](DEPLOY.md) trước khi deploy lên production!
