@echo off
:: aplicar.bat — deja el ERP listo hasta W09 con un solo comando.
:: Ejecutar desde la terminal de VS Code (con env_erp activo), en la carpeta del proyecto.
cd /d "%~dp0"

echo === 1/5 Instalando dependencias ===
python -m pip install -r requirements.txt
if errorlevel 1 goto error

echo === 2/5 Creando migraciones ===
python manage.py makemigrations clientes proveedores configuracion productos ventas
if errorlevel 1 goto error

echo === 3/5 Aplicando migraciones ===
python manage.py migrate
if errorlevel 1 goto error

echo === 4/5 Creando grupos Gerente / Vendedor / Almacen ===
python manage.py crear_grupos
if errorlevel 1 goto error

echo === 5/5 Ejecutando los 108 tests ===
python manage.py test tests --verbosity=1
if errorlevel 1 goto error

echo.
echo ===============================================
echo  LISTO. Proyecto actualizado hasta W09.
echo  Ahora: git add .  ^&^&  git commit  ^&^&  git push
echo ===============================================
goto fin

:error
echo.
echo *** Algo fallo. Copia el mensaje de arriba y pegaselo a Claude. ***

:fin
pause
