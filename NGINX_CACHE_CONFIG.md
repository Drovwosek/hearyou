# Nginx Cache Configuration

## Проблема
При обновлении приложения браузер загружает старую версию из кэша.

## Решение
Настроены правильные HTTP заголовки для автоматической инвалидации кэша.

---

## Конфигурация Nginx

**Файл:** `/etc/nginx/sites-available/hearyou`

### HTML страницы - no-cache (всегда проверять с сервером)

```nginx
location / {
    proxy_pass http://localhost:8000;
    # ... proxy settings ...
    
    # Запретить кэширование HTML
    add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    add_header Pragma "no-cache" always;
    add_header Expires "0" always;
}
```

**Что это значит:**
- `no-cache` - браузер должен проверить с сервером перед использованием кэша
- `no-store` - не сохранять в кэш вообще
- `must-revalidate` - обязательно проверить актуальность

### API endpoints - без кэша

```nginx
location ~ ^/(transcribe|status|result|download|history|stats) {
    proxy_pass http://localhost:8000;
    # ... proxy settings ...
    
    add_header Cache-Control "no-cache, no-store, must-revalidate" always;
}
```

### Статические файлы - долгий кэш с версионированием

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    proxy_pass http://localhost:8000;
    # ... proxy settings ...
    
    add_header Cache-Control "public, max-age=31536000, immutable";
}
```

**Что это значит:**
- `max-age=31536000` - кэш на 1 год (31536000 секунд)
- `immutable` - файл никогда не изменится (для версионированных файлов)

---

## HTML мета-теги

**Файл:** `packages/stt-service/static/index.html`

```html
<head>
    <!-- Cache busting -->
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="version" content="2026-02-27-v2">
</head>
```

**Версия в конце файла:**
```html
<!-- HearYou v2026-02-27-v2 | Updated: 2026-02-27 16:30:00 UTC -->
```

---

## Автоматическое обновление версии

**Скрипт:** `packages/stt-service/update-version.sh`

```bash
#!/bin/bash
VERSION=$(date -u +%Y-%m-%d-%H%M%S)

# Обновить meta-тег version
sed -i "s/name=\"version\" content=\"[^\"]*\"/name=\"version\" content=\"$VERSION\"/" static/index.html

# Обновить комментарий
sed -i "s/<!-- HearYou v[^|]*/<!-- HearYou v$VERSION/" static/index.html
```

**Интеграция в deploy.sh:**
```bash
# 0. Обновление версии (cache busting)
./update-version.sh

# 1. Деплой...
rsync ...
docker-compose up ...
```

---

## Как работает

### До обновления:
1. Пользователь открывает https://92.51.36.233
2. Браузер загружает HTML из кэша (старая версия)
3. Результат: видит старый UI ❌

### После обновления:
1. Пользователь открывает https://92.51.36.233
2. Браузер видит `Cache-Control: no-cache`
3. Браузер проверяет с сервером: "Есть новая версия?"
4. Сервер: "Да! Вот новая версия с version=2026-02-27-163000"
5. Браузер загружает новую версию
6. Результат: видит новый UI ✅

---

## Проверка

### В браузере (DevTools):

1. F12 → Network
2. Обновить страницу (F5)
3. Кликнуть на запрос `/ (document)`
4. Response Headers:
   ```
   Cache-Control: no-cache, no-store, must-revalidate
   Pragma: no-cache
   Expires: 0
   ```

### В HTML (View Source):

```html
<meta name="version" content="2026-02-27-163000">
...
<!-- HearYou v2026-02-27-163000 | Updated: 2026-02-27 16:30:00 UTC -->
```

---

## Важно

❗ **Применить на production сервере:**

```bash
# 1. Обновить nginx конфигурацию
sudo nano /etc/nginx/sites-available/hearyou
# (вставить новые location блоки)

# 2. Проверить синтаксис
sudo nginx -t

# 3. Перезагрузить nginx
sudo systemctl reload nginx

# 4. Обновить HTML в контейнере
docker cp packages/stt-service/static/index.html hearyou-stt:/app/static/index.html
```

---

## Альтернативные методы (не используются)

### 1. Query string versioning
```html
<link rel="stylesheet" href="style.css?v=20260227">
```
❌ Работает, но требует изменять HTML при каждом обновлении CSS/JS

### 2. Content-based hashing
```html
<link rel="stylesheet" href="style.abc123def.css">
```
❌ Требует билд-систему (Webpack, Vite, etc.)

### 3. Service Worker
```js
self.addEventListener('fetch', event => { ... })
```
❌ Сложно, требует HTTPS + PWA manifest

---

## Итог

✅ **Текущее решение:**
- Простое
- Работает сразу
- Не требует билд-системы
- Автоматизировано через deploy.sh
- Браузер всегда загружает актуальную версию

🎉 **Больше не нужен Ctrl+Shift+R!**
