@echo off
for /f "tokens=1-3 delims=/." %%a in ("%DATE%") do set today=%%a_%%b_%%c
docker exec -t PostgreSQL_DB pg_dump -U postgres -d trips_db > backup_%today%.sql
echo Backup is ready!
pause