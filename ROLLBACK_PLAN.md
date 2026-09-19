# Rollback Plan — OsintNeoAi Spark Intelligence Engine

## Trigger Conditions
- Email delivery fails for 2+ consecutive runs
- Gemini API errors persist (429/503 beyond retry limits)
- Digest content quality degrades significantly
- Security vulnerability discovered in dependencies

## Rollback Steps

### Option 1: Disable Workflow (Immediate)
```bash
gh workflow disable "Spark Intelligence Engine (Daily)" --repo brainmedus-arch/OsintNeoAi
```
**Time to rollback:** < 1 minute

### Option 2: Revert to Previous Version
```bash
cd C:\OsintNeoAi
git log --oneline -5  # Find last working commit
git revert <commit-hash>
git push
```
**Time to rollback:** < 5 minutes

### Option 3: Redeploy Previous Version
```bash
git checkout <last-good-commit> -- spark_intelligence_engine.py
git commit -m "Rollback: revert to last known good version"
git push
```
**Time to rollback:** < 5 minutes

## Verification After Rollback
1. Check workflow status: `gh run list --repo brainmedus-arch/OsintNeoAi`
2. Verify email delivery: Check `amd949609@gmail.com` for digest
3. Check error logs: `gh run view <run-id> --repo brainmedus-arch/OsintNeoAi`

## Database Considerations
- No database migrations involved
- CSV file (`SPARK_Correlations.csv`) is append-only
- Digests are stored in `reports/spark_digests/` — can be pruned if needed

## Communication
- Notify via email if rollback affects digest delivery
- Log rollback in `reports/` directory

## Pre-Launch Checklist Status
- [x] All tests pass (syntax validation)
- [x] Build succeeds with no warnings
- [x] No secrets in code or version control
- [x] Error handling covers expected failure modes (429/503 retries)
- [x] Environment variables set in production (GitHub Secrets)
- [x] Logging and error reporting configured
- [x] Health check: email delivery confirms success
- [x] Rollback plan documented (this file)
