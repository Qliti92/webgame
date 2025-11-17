#!/usr/bin/env python
"""
Development server script - Chạy server development không cần Docker
Chỉ dùng cho development/testing, KHÔNG dùng cho production!
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and print output"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}\n")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"\n❌ Lỗi khi chạy: {description}")
        return False
    return True

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         GAME TOPUP - Development Server                  ║
    ║                                                          ║
    ║  LƯU Ý: Script này chỉ dùng cho development/testing!    ║
    ║  Để chạy production, vui lòng dùng Docker!              ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # Change to backend directory
    os.chdir('backend')

    print("\n📋 Các bước sẽ thực hiện:")
    print("1. Cài đặt dependencies")
    print("2. Chạy migrations")
    print("3. Tạo superuser (nếu cần)")
    print("4. Collect static files")
    print("5. Chạy development server")

    response = input("\n▶ Tiếp tục? (y/n): ")
    if response.lower() != 'y':
        print("Đã hủy.")
        return

    # Step 1: Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Cài đặt dependencies"
    ):
        return

    # Step 2: Run migrations
    if not run_command(
        f"{sys.executable} manage.py migrate",
        "Chạy database migrations"
    ):
        print("\n⚠️  Lỗi migration. Bạn có thể cần:")
        print("   - Cài đặt PostgreSQL và cập nhật DATABASE_URL trong .env")
        print("   - Hoặc dùng SQLite cho dev (sửa settings.py)")
        response = input("\n▶ Tiếp tục bỏ qua lỗi? (y/n): ")
        if response.lower() != 'y':
            return

    # Step 3: Create superuser
    print("\n" + "="*60)
    print("👤 Tạo superuser")
    print("="*60)
    response = input("\n▶ Bạn muốn tạo superuser? (y/n): ")
    if response.lower() == 'y':
        subprocess.run(f"{sys.executable} manage.py createsuperuser", shell=True)

    # Step 4: Collect static files
    run_command(
        f"{sys.executable} manage.py collectstatic --noinput",
        "Collect static files"
    )

    # Step 5: Run development server
    print("\n" + "="*60)
    print("🚀 Khởi động Development Server")
    print("="*60)
    print("\n📱 Server sẽ chạy tại: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/api/docs/")
    print("⚙️  Admin Panel: http://127.0.0.1:8000/admin/")
    print("\nNhấn Ctrl+C để dừng server\n")

    try:
        subprocess.run(f"{sys.executable} manage.py runserver", shell=True)
    except KeyboardInterrupt:
        print("\n\n👋 Đã dừng server. Tạm biệt!")

if __name__ == '__main__':
    main()
