@echo off
echo ========================================
echo  DEPLOYING CRYPTO PAYMENT SYSTEM (FLOW 3)
echo ========================================
echo.
echo Changes to deploy:
echo - CryptoDeposit model + admin interface
echo - Crypto deposit API endpoints
echo - Order payment flow updates
echo - Frontend crypto payment modal
echo ========================================
echo.

echo Step 1: Stopping services...
docker-compose down

echo.
echo Step 2: Rebuilding backend with new code...
docker-compose build backend

echo.
echo Step 3: Starting all services...
docker-compose up -d

echo.
echo Step 4: Waiting for services to be ready...
timeout /t 10 /nobreak

echo.
echo Step 5: Running migrations (CryptoDeposit model)...
docker-compose exec backend python manage.py migrate wallets

echo.
echo Step 6: Running all migrations...
docker-compose exec backend python manage.py migrate

echo.
echo Step 7: Collecting static files...
docker-compose exec backend python manage.py collectstatic --noinput

echo.
echo ========================================
echo  DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Crypto Payment Flow 3 is now live!
echo.
echo Admin tasks:
echo 1. Go to: http://localhost/admin/wallets/cryptodeposit/
echo 2. When users submit deposits, use action: "Confirm selected crypto deposits"
echo 3. System will auto-pay related orders
echo.
echo User flow:
echo 1. Create order
echo 2. Select "Crypto" payment
echo 3. Fill deposit form with TX hash
echo 4. Wait for admin confirmation
echo 5. Order auto-paid from wallet
echo.
echo Files deployed:
echo Backend (7 files):
echo   - apps/wallets/models.py (CryptoDeposit model)
echo   - apps/wallets/admin.py (admin interface)
echo   - apps/wallets/serializers.py (API serializers)
echo   - apps/wallets/views.py (API views)
echo   - apps/wallets/urls.py (API URLs)
echo   - apps/orders/models.py (total_amount property)
echo   - apps/orders/views.py (payment flow)
echo Frontend (2 files):
echo   - templates/wallet/deposit.html
echo   - templates/orders/detail.html
echo Migration:
echo   - wallets/0004_cryptodeposit.py
echo.
echo View logs:
echo   docker-compose logs -f backend
echo.
pause
