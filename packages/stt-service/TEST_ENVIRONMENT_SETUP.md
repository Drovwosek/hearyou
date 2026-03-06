# Test Environment Setup Documentation

## 📋 Overview

This document describes the test environment setup for the HearYou STT service, including the nginx proxy configuration and speaker formatting fix.

**Date:** 2026-03-06  
**Status:** ✅ Active

---

## 🌐 Access URLs

### Production Environment
- **URL:** https://92.51.36.233/
- **Container:** `hearyou-stt`
- **Port:** 8000
- **Static files:** `/root/.openclaw/workspace/hearyou/packages/stt-service/static/`
- **Status:** **STABLE** - No changes made

### Test Environment
- **URL:** https://92.51.36.233/test/
- **Container:** `hearyou-stt-test`
- **Port:** 8001
- **Static files:** `/root/.openclaw/workspace/hearyou/packages/stt-service/static-test/`
- **Status:** **TESTING** - Contains speaker formatting fix

---

## 🔧 Infrastructure Changes

### 1. Nginx Reverse Proxy Configuration

**File:** `/etc/nginx/sites-available/hearyou`

**Added location block:**
```nginx
# TEST ENVIRONMENT - /test/ -> localhost:8001
location /test/ {
    proxy_pass http://localhost:8001/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
    
    proxy_read_timeout 7200s;
    proxy_connect_timeout 7200s;
    proxy_send_timeout 7200s;
    
    # Запретить кэширование HTML
    add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    add_header Pragma "no-cache" always;
    add_header Expires "0" always;
}
```

**How it works:**
- Requests to `/test/` are proxied to `localhost:8001/` (test container)
- Path is rewritten: `/test/transcribe` → `/transcribe` on port 8001
- All production settings (timeouts, headers) are preserved

**Reload command:**
```bash
nginx -t && systemctl reload nginx
```

---

### 2. Docker Compose Test Configuration

**File:** `/root/.openclaw/workspace/hearyou/packages/stt-service/docker-compose.test.yml`

**Key changes:**
```yaml
volumes:
  - ./static-test:/app/static:ro  # ← Changed from ./static
```

**Separate data directories for test:**
- `uploads-test/` - Test file uploads
- `results-test/` - Test transcription results
- `temp-test/` - Test temporary files
- `logs-test/` - Test logs
- `static-test/` - **Test frontend with fixes**

**Start/stop commands:**
```bash
cd /root/.openclaw/workspace/hearyou/packages/stt-service

# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Stop test environment
docker-compose -f docker-compose.test.yml down

# View logs
docker-compose -f docker-compose.test.yml logs -f
```

---

## 🐛 Speaker Formatting Fix

### Problem

**Original behavior:**
- API returns word-by-word speaker labels:  
  `"SPEAKER_0: word1 word2 SPEAKER_1: word3 word4 SPEAKER_0: word5..."`

- Frontend `formatSpeakers()` function expects blocks separated by `\n\n`:
  ```
  SPEAKER_0: sentence from speaker 0
  
  SPEAKER_1: sentence from speaker 1
  
  SPEAKER_0: another sentence from speaker 0
  ```

- **Result:** Each word appeared as a separate colored block instead of aggregated sentences.

### Solution

**Added preprocessing function in `static-test/index.html`:**

```javascript
function aggregateSpeakerText(text) {
    /**
     * Преобразует текст с word-by-word speaker labels в блоки по спикерам.
     * Входной формат: "SPEAKER_0: word1 word2 SPEAKER_1: word3 word4..."
     * Выходной формат: "SPEAKER_0: word1 word2\n\nSPEAKER_1: word3 word4\n\n..."
     */
    
    const pattern = /(?:SPEAKER_(\d+)|Спикер (\d+)):\s*/g;
    const parts = text.split(pattern);
    
    let blocks = [];
    let currentSpeaker = null;
    let currentText = "";
    
    for (let i = 1; i < parts.length; i += 3) {
        const speakerNum = parts[i] || parts[i + 1];
        const textPart = parts[i + 2] || "";
        
        if (!speakerNum) continue;
        
        const speaker = `SPEAKER_${speakerNum}`;
        
        if (currentSpeaker === speaker) {
            // Same speaker - append text
            currentText += " " + textPart.trim();
        } else {
            // New speaker - save previous block
            if (currentSpeaker && currentText.trim()) {
                blocks.push(`${currentSpeaker}: ${currentText.trim()}`);
            }
            currentSpeaker = speaker;
            currentText = textPart.trim();
        }
    }
    
    // Save last block
    if (currentSpeaker && currentText.trim()) {
        blocks.push(`${currentSpeaker}: ${currentText.trim()}`);
    }
    
    return blocks.join("\n\n");
}
```

**Usage in `showResult()` function:**
```javascript
// Before (production):
resultText.innerHTML = legend + formatSpeakers(text);

// After (test):
const aggregatedText = aggregateSpeakerText(text);
resultText.innerHTML = legend + formatSpeakers(aggregatedText);
```

### Expected Result

✅ **With fix (test environment):**
- Consecutive words from the same speaker are grouped together
- Each speaker turn appears as one colored bubble
- Clean, readable conversation format with avatars and speaker labels

❌ **Without fix (production):**
- Each word might appear as a separate bubble
- Excessive visual noise
- Harder to follow conversation flow

---

## 🧪 Testing Instructions

### 1. Upload a file with speaker labeling

**Production test:**
1. Go to https://92.51.36.233/
2. Upload an audio file with multiple speakers
3. ✅ Enable "🎭 Определить спикеров"
4. Click "📤 Загрузить и транскрибировать"
5. **Expected:** Word-by-word speaker labels (current behavior)

**Test environment:**
1. Go to https://92.51.36.233/test/
2. Upload the **same audio file**
3. ✅ Enable "🎭 Определить спикеров"
4. Click "📤 Загрузить и транскрибировать"
5. **Expected:** Aggregated speaker blocks with colored bubbles

### 2. Compare results

**Production:** Each word/phrase might be separate  
**Test:** Sentences grouped by speaker with visual formatting

---

## 📁 File Structure

```
/root/.openclaw/workspace/hearyou/packages/stt-service/
├── static/              # Production frontend (UNCHANGED)
│   └── index.html       # Original version
├── static-test/         # Test frontend (WITH FIX)
│   └── index.html       # Fixed version with aggregateSpeakerText()
├── docker-compose.yml   # Production (port 8000)
├── docker-compose.test.yml  # Test (port 8001)
├── uploads/             # Production uploads
├── uploads-test/        # Test uploads
├── results/             # Production results
├── results-test/        # Test results
├── logs/                # Production logs
└── logs-test/           # Test logs
```

---

## ✅ Verification Checklist

- [x] Nginx config updated with `/test/` location
- [x] Nginx reloaded successfully
- [x] Test container using separate `static-test/` folder
- [x] Production container using original `static/` folder
- [x] `aggregateSpeakerText()` function present in test only
- [x] Both environments accessible via HTTPS
- [x] Production environment unchanged and stable

**Verification commands:**
```bash
# Check nginx config
cat /etc/nginx/sites-available/hearyou | grep -A 10 "TEST ENVIRONMENT"

# Check containers
docker ps | grep hearyou

# Verify production has NO aggregateSpeakerText
curl -k -s https://92.51.36.233/ | grep -c "aggregateSpeakerText"
# Output: 0

# Verify test HAS aggregateSpeakerText
curl -k -s https://92.51.36.233/test/ | grep -c "aggregateSpeakerText"
# Output: 2
```

---

## 🚀 Rollout Plan

### If test is successful:

1. **Copy the fix to production:**
   ```bash
   cd /root/.openclaw/workspace/hearyou/packages/stt-service
   cp static-test/index.html static/index.html
   ```

2. **No container restart needed** - nginx serves files directly

3. **Verify production:**
   ```bash
   curl -k -s https://92.51.36.233/ | grep -c "aggregateSpeakerText"
   # Should output: 2
   ```

### If issues found:

1. **Revert test environment:**
   ```bash
   cd /root/.openclaw/workspace/hearyou/packages/stt-service
   cp static/index.html.backup static-test/index.html
   docker-compose -f docker-compose.test.yml restart
   ```

2. **Production remains untouched** - no rollback needed

---

## 📝 Notes

- Production environment is **completely isolated** - no changes made
- Test environment shares backend (Yandex STT, database) but has separate:
  - Frontend files
  - Upload/result/temp directories
  - Logs
- SSL certificate is self-signed (same for both environments)
- Both environments use the same `.env.yandex` and `.env.huggingface` files

---

## 🔗 Related Files

- `/etc/nginx/sites-available/hearyou` - Nginx configuration
- `/root/.openclaw/workspace/hearyou/packages/stt-service/static-test/index.html` - Fixed frontend
- `/root/.openclaw/workspace/hearyou/packages/stt-service/docker-compose.test.yml` - Test container config

---

**Last updated:** 2026-03-06 09:23 UTC  
**Author:** OpenClaw Agent (subagent)
