#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
backup="$(mktemp -d)"
trap 'rm -rf "$backup"' EXIT
cp -R lib "$backup/lib"
cp pubspec.yaml analysis_options.yaml "$backup/"
flutter create --project-name core_strength_mobile --org com.corestrength --platforms android,ios,web .
rm -rf lib
cp -R "$backup/lib" ./lib
cp "$backup/pubspec.yaml" "$backup/analysis_options.yaml" .
flutter pub get
printf '\nĐã tạo platform. Chạy thử bằng: flutter run\n'
