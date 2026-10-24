@echo off
title MoneyLeak - Push to GitHub & Deploy to Vercel
cd /d "%~dp0"
echo ========================================================
echo   MoneyLeak Deployment Automation
echo ========================================================
echo.
echo Staging and committing changes...
git add -A
git diff-index --quiet HEAD || git commit -m "fix(theme): persist light theme across page transitions, universal sync, and transactions"
echo.
echo Pushing latest commits to GitHub (shailendrathakur3008/MoneyLeak)...
echo.
echo If GitHub Credential Manager pops up, click 'Sign in with browser'.
echo.
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Code pushed successfully to GitHub!
    echo.
    echo Triggering Vercel automatic deployment...
    powershell -Command "try { $res = Invoke-RestMethod -Uri 'https://api.vercel.com/v1/integrations/deploy/prj_Zjbwao7f4dTJRyKDAVZQWIumUPWa/JcscowpwzJ' -Method Post; Write-Host 'Vercel Deployment Job ID:' $res.job.id 'State:' $res.job.state } catch { Write-Host 'Error triggering hook:' $_ }"
    echo.
    echo ========================================================
    echo   Deployment initiated!
    echo   Check: https://moneyleak-tau.vercel.app
    echo ========================================================
) else (
    echo.
    echo [WARNING] Git push did not complete. If prompted, please complete
    echo the GitHub login in your browser and run this file again.
)
echo.
pause
