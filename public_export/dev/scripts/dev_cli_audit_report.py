import json
import os
import shutil
import subprocess
from datetime import datetime

def run_dev_cli_audit():
    clis = ['uv', 'node', 'npm', 'gcloud', 'bq', 'firebase', 'adb', 'rclone', 'git', 'python']
    status = {}

    for cli in clis:
        path = shutil.which(cli)
        if path:
            try:
                res = subprocess.run([cli, '--version'], capture_output=True, text=True, timeout=5)
                ver = (res.stdout or res.stderr or 'Installed').strip().split('\n')[0]
            except Exception:
                ver = 'Installed'
            status[cli] = {'installed': True, 'path': path, 'version': ver}
        else:
            status[cli] = {'installed': False, 'path': None, 'version': 'MISSING'}

    audit_payload = {
        "status": "COMPLETED",
        "audited_at": datetime.now().isoformat(),
        "total_clis_audited": len(clis),
        "all_clis_healthy": all(item['installed'] for item in status.values()),
        "clis": status
    }

    out_v1 = r"C:\Amd949609_Antigravity_v1\docs\DEV_CLI_AUDIT_REPORT.json"
    out_repo = r"C:\OsintNeoAi\reports\DEV_CLI_AUDIT_REPORT.json"

    os.makedirs(os.path.dirname(out_v1), exist_ok=True)
    os.makedirs(os.path.dirname(out_repo), exist_ok=True)

    with open(out_v1, "w", encoding="utf-8") as f:
        json.dump(audit_payload, f, indent=2)

    with open(out_repo, "w", encoding="utf-8") as f:
        json.dump(audit_payload, f, indent=2)

    print(f"Developer CLI Audit complete. Saved report to:\n- {out_v1}\n- {out_repo}")

if __name__ == "__main__":
    run_dev_cli_audit()
