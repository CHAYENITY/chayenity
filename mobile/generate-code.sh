#!/bin/bash

echo "🧊 Generating Freezed and JSON Serialization files..."
echo

echo "📦 Installing dependencies..."
flutter pub get

echo "🔨 Running build_runner..."
dart run build_runner build --delete-conflicting-outputs

echo
echo "✅ Code generation completed!"
echo
echo "📝 Generated files:"
echo "  - *.freezed.dart (Freezed models)"  
echo "  - *.g.dart (JSON serialization)"
echo