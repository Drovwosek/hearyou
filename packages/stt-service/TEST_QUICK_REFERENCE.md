# Test Environment - Quick Reference

## 🌐 Access URLs

| Environment | URL | Container | Port |
|-------------|-----|-----------|------|
| **Production** | https://92.51.36.233/ | hearyou-stt | 8000 |
| **Test** | https://92.51.36.233/test/ | hearyou-stt-test | 8001 |

## 🔧 Management Commands

### Test Container
```bash
cd /root/.openclaw/workspace/hearyou/packages/stt-service

# Start
docker-compose -f docker-compose.test.yml up -d

# Stop
docker-compose -f docker-compose.test.yml down

# Restart
docker-compose -f docker-compose.test.yml restart

# Logs
docker-compose -f docker-compose.test.yml logs -f

# Status
docker ps | grep hearyou
```

### Nginx
```bash
# Reload config (after changes)
nginx -t && systemctl reload nginx

# Check status
systemctl status nginx

# View config
cat /etc/nginx/sites-available/hearyou
```

## 🧪 Testing Speaker Formatting

### Steps:
1. Go to https://92.51.36.233/test/
2. Upload audio with multiple speakers
3. ✅ Enable "🎭 Определить спикеров"
4. Compare with production (https://92.51.36.233/)

### Expected Difference:
- **Production:** Word-by-word speaker labels
- **Test:** Aggregated sentences with colored bubbles & avatars

## 🚀 Rollout to Production

If test is successful:
```bash
cd /root/.openclaw/workspace/hearyou/packages/stt-service
cp static-test/index.html static/index.html
```

No container restart needed! Changes apply immediately.

## 🔙 Rollback Test Environment

If issues found:
```bash
cd /root/.openclaw/workspace/hearyou/packages/stt-service
cp static/index.html.backup static-test/index.html
docker-compose -f docker-compose.test.yml restart
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `/etc/nginx/sites-available/hearyou` | Nginx proxy config |
| `static/index.html` | Production frontend |
| `static-test/index.html` | Test frontend (with fix) |
| `docker-compose.yml` | Production container |
| `docker-compose.test.yml` | Test container |
| `TEST_ENVIRONMENT_SETUP.md` | Full documentation |

## 🔍 Quick Verification

```bash
# Both containers running?
docker ps | grep hearyou-stt

# Production unchanged?
curl -k -s https://92.51.36.233/ | grep -c "aggregateSpeakerText"
# Should return: 0

# Test has fix?
curl -k -s https://92.51.36.233/test/ | grep -c "aggregateSpeakerText"
# Should return: 1 or 2
```

## 💡 What Was Fixed

**Problem:** API returns speaker labels word-by-word, but frontend expected sentence blocks.

**Solution:** Added `aggregateSpeakerText()` function that groups consecutive words from same speaker.

**Location:** Only in `static-test/index.html` (test environment)

---

**Last updated:** 2026-03-06 09:23 UTC
