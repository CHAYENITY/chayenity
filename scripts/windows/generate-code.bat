@echo off
echo 🧊 Generating Freezed and JSON Serialization files...
echo.

cd /d "%~dp0.."

echo 📦 Installing dependencies...
call flutter pub get

echo 🔨 Running build_runner...
call dart run build_runner build --delete-conflicting-outputs

echo.
echo ✅ Code generation completed!
echo.
echo 📝 Generated files:
echo   - *.freezed.dart (Freezed models)  
echo   - *.g.dart (JSON serialization)
echo.

pause