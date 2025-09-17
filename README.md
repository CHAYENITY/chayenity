# 🛍️ Chayenity

[![Status: Final Project](https://img.shields.io/badge/Status-Final%20Project-blue)]()
[![Status: Development](https://img.shields.io/badge/Status-Development-yellow)]()
[![Platform: Mobile](https://img.shields.io/badge/Platform-Mobile-blue)]()

---

## 🛠️ Tech Stack

| Technology | Icon                                                                                                              |
| ---------- | ----------------------------------------------------------------------------------------------------------------- |
| Dart       | ![Dart](https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white)                   |
| Flutter    | ![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)          |
| Python     | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)             |
| FastAPI    | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)          |
| PostgreSQL | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white) |
| Docker     | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)             |

---

## 🚀 Getting Started

### ⬇️ Get dependencies

```bash
cd mobile
flutter pub get
```

### 🚀 Run the app

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

## 🌿 Branch Workflow

- ทุกฟีเจอร์ใหม่ ให้แตก branch จาก `dev` โดยใช้รูปแบบ:

**🌿 Feature Branch**

```bash
feat/<module>/<task-name>
```

**🛠️ Fix Branch**

```bash
fix/<module>/<description>
```

**🚑 Hotfix Branch**

```bash
hotfix/<module>/<critical-issue>
```

**🔄 Refactor Branch**

```bash
refactor/<module>/<description>
```

**⚙️ CI Branch**

```bash
ci/<system>/<task>
```

---

## 🎓 Course Info

- **Course:** `240-331 Mobile Applications Developer Module`
- **Platform:** Mobile
- **Semester:** 1/2025
