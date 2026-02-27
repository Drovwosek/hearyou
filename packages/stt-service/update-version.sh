#!/bin/bash
# Автоматическое обновление версии в index.html

set -e

HTML_FILE="static/index.html"
VERSION=$(date -u +%Y-%m-%d-%H%M%S)

echo "🔄 Обновление версии до: $VERSION"

# Обновить meta-тег version
sed -i "s/name=\"version\" content=\"[^\"]*\"/name=\"version\" content=\"$VERSION\"/" "$HTML_FILE"

# Обновить комментарий в конце файла
sed -i "s/<!-- HearYou v[^|]*/<!-- HearYou v$VERSION/" "$HTML_FILE"
sed -i "s/Updated: [^-]*-->/Updated: $(date -u +%Y-%m-%d\ %H:%M:%S\ UTC) -->/" "$HTML_FILE"

echo "✅ Версия обновлена: $VERSION"
echo "📄 Файл: $HTML_FILE"
