#!/usr/bin/env bash
# ip_watch.sh — auto-ingest new GitHub pushes of OsintNeoAi into the IP sweep.
# Watches ALL refs (branches produced by OpenCode sessions included); when any
# branch changes, fetches the changed branches shallowly, ingests the newest one,
# and pushes the fresh dossier set to GCS.
#
# Cron: 23 */6 * * *   (temporary 5-minute cadence while a known push is landing)
# State: .refs_state (fingerprint) + .refs_snapshot (last ls-remote listing)
set -u
REPO=/home/osintneoai/repos/OsintNeoAi
STATE=/home/osintneoai/tools/ip_intake/.refs_state
SNAP=/home/osintneoai/tools/ip_intake/.refs_snapshot
TOOL=/home/osintneoai/tools/ip_intake/ip_ingest.py
EVID=/home/osintneoai/evidence/ip_intake
PUSH=/home/osintneoai/tools/cloud_backup/cloud_backup.sh
LOG=/home/osintneoai/tools/ip_intake/watch.log

log() { echo "$(date -u +%FT%TZ) $*" >> "$LOG"; }

REMOTE_REFS=$(timeout 60 git ls-remote https://github.com/Tonypost949/OsintNeoAi.git 2>/dev/null | sort)
[ -z "${REMOTE_REFS:-}" ] && { log "ls-remote failed (network?)"; exit 0; }
FP=$(printf '%s' "$REMOTE_REFS" | sha256sum | awk '{print $1}')
if [ -f "$STATE" ] && [ "$(cat "$STATE")" = "$FP" ]; then
  exit 0
fi

CHANGED=""
if [ -f "$SNAP" ]; then
  CHANGED=$(comm -13 <(sort "$SNAP") <(printf '%s\n' "$REMOTE_REFS") | awk '$2 ~ /^refs\/heads\// {print $2}')
else
  CHANGED=$(printf '%s\n' "$REMOTE_REFS" | awk '$2 ~ /^refs\/heads\// {print $2}')
fi
if [ -z "$CHANGED" ]; then
  printf '%s\n' "$REMOTE_REFS" > "$SNAP"
  echo "$FP" > "$STATE"
  exit 0
fi

cd "$REPO" || { log "repo missing"; exit 0; }
log "changed refs: $(echo "$CHANGED" | tr '\n' ' ')"
BEST=""
BEST_TS=0
for ref in $CHANGED; do
  br=${ref#refs/heads/}
  if timeout 300 git fetch --depth 1 origin "+$ref:refs/remotes/origin/$br" >>"$LOG" 2>&1; then
    ts=$(git log -1 --format=%ct "refs/remotes/origin/$br" 2>/dev/null || echo 0)
    log "  fetched $br (commit ts $ts)"
    if [ "${ts:-0}" -gt "$BEST_TS" ]; then BEST="$br"; BEST_TS="$ts"; fi
  else
    log "  fetch failed: $br"
  fi
done
if [ -z "$BEST" ]; then
  log "no branch fetched successfully - will retry next cycle"
  exit 0
fi

if ! git checkout --detach "refs/remotes/origin/$BEST" >>"$LOG" 2>&1; then
  log "checkout failed for $BEST"
  exit 0
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
SAFE=${BEST//\//_}
OUT="$EVID/${STAMP}_ghpush_${SAFE}"
mkdir -p "$OUT"
if ! python3 "$TOOL" --root "$REPO" --out "$OUT" --label "osintneoai_ghpush_${STAMP}_${SAFE}" >>"$LOG" 2>&1; then
  log "ingest failed for branch $BEST"
  exit 0
fi
"$PUSH" push-path "$OUT" "ip_sweep_${STAMP}_${SAFE}" >>"$LOG" 2>&1
printf '%s\n' "$REMOTE_REFS" > "$SNAP"
echo "$FP" > "$STATE"
log "ingested branch $BEST (ts $BEST_TS) -> $OUT"
