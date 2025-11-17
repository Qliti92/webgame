# Hướng Dẫn Deploy Lên VPS Ubuntu

## Yêu Cầu Hệ Thống

- Ubuntu 20.04/22.04 LTS
- RAM tối thiểu: 2GB
- Disk: 20GB+
- Docker và Docker Compose đã cài đặt

## Bước 1: Cài Đặt Docker và Docker Compose

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker-compose --version
```

**Logout và login lại để áp dụng group docker**

## Bước 2: Upload Code Lên VPS

### Cách 1: Sử dụng Git (Khuyên dùng)

```bash
# Clone repository
git clone YOUR_REPOSITORY_URL /var/www/webgame
cd /var/www/webgame
```

### Cách 2: Sử dụng SCP

```bash
# Trên máy local
scp -r /path/to/WEBGAME user@your-vps-ip:/var/www/webgame
```

## Bước 3: Cấu Hình Environment

```bash
cd /var/www/webgame

# Copy file .env.production.example sang .env
cp .env.production.example .env

# Chỉnh sửa file .env
nano .env
```

### Các Giá Trị CẦN PHẢI ĐỔI trong .env:

```bash
# 1. Generate SECRET_KEY mới
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 2. Generate JWT_SECRET_KEY mới
openssl rand -base64 64

# 3. Cập nhật trong .env:
SECRET_KEY=<secret-key-mới-generate-ở-trên>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

DATABASE_URL=postgresql://gameuser:STRONG_PASSWORD@db:5432/gamedb
POSTGRES_PASSWORD=STRONG_PASSWORD  # Đổi password mạnh

JWT_SECRET_KEY=<jwt-key-mới-generate-ở-trên>

CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 4. Cập nhật thông tin wallet và email
ADMIN_USDT_TRC20_ADDRESS=YOUR-REAL-WALLET
TRON_API_KEY=YOUR-TRONGRID-KEY
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Bước 4: Build và Chạy Containers

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Kiểm tra logs
docker-compose -f docker-compose.prod.yml logs -f

# Kiểm tra containers đang chạy
docker-compose -f docker-compose.prod.yml ps
```

## Bước 5: Tạo Superuser

```bash
# Tạo Django superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Bước 6: Cấu Hình Firewall

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22

# Allow HTTP và HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Check status
sudo ufw status
```

## Bước 7: Cấu Hình SSL (HTTPS) - Tùy Chọn Nhưng Khuyên Dùng

### Sử dụng Let's Encrypt (Miễn phí)

```bash
# Install Certbot
sudo apt install -y certbot

# Generate SSL certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates sẽ được lưu tại: /etc/letsencrypt/live/yourdomain.com/
```

### Cập nhật Nginx config cho HTTPS

Tạo file `nginx/nginx.prod.conf`:

```nginx
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream backend {
        server backend:8000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;
        client_max_body_size 10M;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        location /static/ {
            alias /app/staticfiles/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /app/media/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
        }
    }
}
```

Cập nhật docker-compose.prod.yml để mount SSL certificates:

```yaml
nginx:
  volumes:
    - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
    - /etc/letsencrypt/live/yourdomain.com:/etc/nginx/ssl:ro
    - static_volume:/app/staticfiles
    - media_volume:/app/media
```

## Bước 8: Maintenance Commands

### Xem logs
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f celery
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Restart services
```bash
docker-compose -f docker-compose.prod.yml restart
docker-compose -f docker-compose.prod.yml restart backend
```

### Update code
```bash
cd /var/www/webgame
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### Backup database
```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U gameuser gamedb > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore database
```bash
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U gameuser gamedb
```

## Bước 9: Monitoring và Auto-restart

### Cài đặt auto-start khi server reboot

Tạo file `/etc/systemd/system/webgame.service`:

```bash
sudo nano /etc/systemd/system/webgame.service
```

Nội dung:

```ini
[Unit]
Description=Web Game Platform
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/var/www/webgame
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable service:

```bash
sudo systemctl enable webgame
sudo systemctl start webgame
sudo systemctl status webgame
```

## Troubleshooting

### Container không start
```bash
docker-compose -f docker-compose.prod.yml logs
docker-compose -f docker-compose.prod.yml ps
```

### Database connection error
- Kiểm tra DATABASE_URL trong .env
- Kiểm tra PostgreSQL container đang chạy: `docker-compose -f docker-compose.prod.yml ps db`

### Static files không load
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
docker-compose -f docker-compose.prod.yml restart nginx
```

### Permission denied errors
```bash
sudo chown -R $USER:$USER /var/www/webgame
```

## Security Checklist

- [ ] DEBUG=False trong .env
- [ ] SECRET_KEY và JWT_SECRET_KEY đã đổi
- [ ] ALLOWED_HOSTS đã cập nhật đúng domain
- [ ] Database password đã đổi mạnh
- [ ] Firewall đã enable
- [ ] SSL certificate đã cài đặt
- [ ] File .env không commit lên git
- [ ] Sentry DSN đã cấu hình (optional)

## Liên Hệ & Support

Nếu gặp vấn đề, vui lòng kiểm tra logs và documentation.
