# Auto-Sync Script for VM / VPS / Local Environments
# Uses git & standard system cron (Linux/Termux) or Windows Scheduled Tasks
# 100% Free - Consumes $0.00 credits, no API fees, no paid services.

echo "[`date`] Starting OsintNeoAi Vector Node Sync..."
cd /path/to/OsintNeoAi || cd C:\OsintNeoAi
git pull origin main --quiet
echo "[`date`] OsintNeoAi Vector Node Sync Complete."
