@echo off
setlocal
set LOG=%TEMP%\fix-mysql-service.log
echo ==== fix-mysql-service start %DATE% %TIME% ==== > "%LOG%"
whoami >> "%LOG%" 2>&1
whoami /groups | findstr /i "S-1-16" >> "%LOG%" 2>&1
echo ---- mysqld exe check ---- >> "%LOG%" 2>&1
dir "D:\dbs\mysql-8.4.11-winx64\bin\mysqld.exe" >> "%LOG%" 2>&1
echo ---- current mysqld processes ---- >> "%LOG%" 2>&1
tasklist | findstr /i mysqld >> "%LOG%" 2>&1
echo ---- shutdown existing instance if any ---- >> "%LOG%" 2>&1
"D:\dbs\mysql-8.4.11-winx64\bin\mysqladmin.exe" -h 127.0.0.1 -u root -p123456 shutdown >> "%LOG%" 2>&1
ping -n 6 127.0.0.1 > nul
echo ---- taskkill leftover mysqld ---- >> "%LOG%" 2>&1
taskkill /f /im mysqld.exe >> "%LOG%" 2>&1
ping -n 3 127.0.0.1 > nul
echo ---- sc qc before ---- >> "%LOG%" 2>&1
sc.exe qc MySQL84 >> "%LOG%" 2>&1
echo ---- sc config binPath ---- >> "%LOG%" 2>&1
sc.exe config MySQL84 binPath= "\"D:\dbs\mysql-8.4.11-winx64\bin\mysqld.exe\" --defaults-file=D:\dbs\mysql-8.4.11-winx64\my.ini MySQL84" >> "%LOG%" 2>&1
echo SC_CONFIG_EXIT=%ERRORLEVEL% >> "%LOG%" 2>&1
sc.exe config MySQL84 start= auto >> "%LOG%" 2>&1
echo SC_STARTTYPE_EXIT=%ERRORLEVEL% >> "%LOG%" 2>&1
echo ---- sc qc after ---- >> "%LOG%" 2>&1
sc.exe qc MySQL84 >> "%LOG%" 2>&1
echo ---- start service ---- >> "%LOG%" 2>&1
sc.exe start MySQL84 >> "%LOG%" 2>&1
echo SC_START_EXIT=%ERRORLEVEL% >> "%LOG%" 2>&1
ping -n 9 127.0.0.1 > nul
echo ---- sc query final ---- >> "%LOG%" 2>&1
sc.exe query MySQL84 >> "%LOG%" 2>&1
echo ---- port 3306 ---- >> "%LOG%" 2>&1
netstat -ano | findstr :3306 >> "%LOG%" 2>&1
echo ==== end %DATE% %TIME% ==== >> "%LOG%"
copy /y "%LOG%" "D:\pro\goodzheng-pro\.qoder\scripts\fix-mysql-service.log" > nul 2>&1
exit /b 0
