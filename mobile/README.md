# ✨ Quickstart ✨

## ⬇️ Get dependencies ⬇️

```bash
flutter pub get
```

## 🧊 Generate Freezed & JSON Files 🧊

After installing dependencies, generate the required Freezed and JSON serialization files:

```bash
dart run build_runner build --delete-conflicting-outputs
```

**Windows:**

```bash
generate-code.bat
```

**Linux/macOS:**

```bash
chmod +x generate-code.sh
./generate-code.sh
```

**Manual:**

```bash
# One-time generation
dart run build_runner build --delete-conflicting-outputs

# Watch mode (auto-regenerate on file changes)
dart run build_runner watch --delete-conflicting-outputs
```

> **⚠️ Important:** You must run code generation whenever you:
>
> - Add new `@freezed` models
> - Modify existing Freezed models
> - Change JSON annotations (`@JsonKey`)
> - First time setting up the project

---

## 🚀 Run the app 🚀

- `macOS, iOS`

```bash
open ios/Runner.xcworkspace
```

```bash
xcrun simctl list devices
xcrun simctl boot "iPhone 16"
```

```bash
open -a Simulator
```

```bash
flutter run
```

---

## 🧹 Format & Lint 🧹

```bash
dart analyze
```

```bash
dart format .
```
