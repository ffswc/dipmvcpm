@echo off
chcp 65001 > nul
set "ROLLS_DIR=%~dp0rolls"

echo 正在自动更新胶片索引网页...

:: 创建或清空 temp.html
set "TEMP_FILE=%ROLLS_DIR%\index.html"

:: 写入 HTML 头部
(
echo ^<!DOCTYPE html^>
echo ^<html lang="zh-CN"^>
echo ^<head^>
echo ^<meta charset="UTF-8"^>
echo ^<meta name="viewport" content="width=device-width, initial-scale=1.0"^>
echo ^<title^>Film Rolls Index^</title^>
echo ^<style^>
echo body { margin: 0; background: #111; color: #ddd; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
echo h1 { text-align: center; font-size: 18px; margin: 16px 0 6px; font-weight: 500; }
echo .note { text-align: center; font-size: 12px; color: #777; margin-bottom: 14px; }
echo .list { max-width: 720px; margin: 0 auto; padding: 0 10px 30px; }
echo .roll { display: flex; justify-content: space-between; align-items: center; padding: 12px 10px; border-bottom: 1px solid #222; text-decoration: none; color: #ddd; }
echo .roll:hover { background: #181818; }
echo .roll span { font-size: 14px; letter-spacing: 0.3px; }
echo .roll small { font-size: 11px; color: #888; }
echo ^</style^>
echo ^</head^>
echo ^<body^>
echo ^<h1^>Film Rolls^</h1^>
echo ^<div class="note"^>Noritsu HS1800 · Roll Archive^</div^>
echo ^<div class="list"^>
) > "%TEMP_FILE%"

:: 遍历 rolls 文件夹下的所有文件夹并写入链接
for /d %%D in ("%ROLLS_DIR%\*") do (
    echo   ^<a class="roll" href="./%%~nxD/"^> >> "%TEMP_FILE%"
    echo     ^<span^>%%~nxD^</span^> >> "%TEMP_FILE%"
    echo     ^<small^>Roll^</small^> >> "%TEMP_FILE%"
    echo   ^</a^> >> "%TEMP_FILE%"
)

:: 写入 HTML 尾部
(
echo ^</div^>
echo ^</body^>
echo ^</html^>
) >> "%TEMP_FILE%"

echo ✅ 网页更新完成！
echo.
pause