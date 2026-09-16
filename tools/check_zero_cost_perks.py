import os
import sys
import json
from datetime import datetime

ZERO_COST_RESOURCES = {
    "edu_account": "anthony.dimarcello@students.post.edu",
    "google_cloud_always_free": {
        "bigquery": "10 GB storage + 1 TB query processing per month (FREE forever)",
        "cloud_shell": "100% Free 5GB persistent Linux VM & Web Preview (https://shell.cloud.google.com)",
        "cloud_run": "2 Million requests / 360,000 GB-seconds per month FREE",
        "cloud_functions": "2 Million invocations per month FREE",
        "gcs": "5 GB-months standard storage FREE"
    },
    "google_ai_free_tier": {
        "ai_studio_gemini_api": "15 RPM, 1M TPM, 1,500 RPD FREE (https://aistudio.google.com)",
        "google_colab": "Free T4 GPU & TPU notebook acceleration (https://colab.research.google.com)",
        "kaggle_gpu_tpu": "30 hrs/wk free P100/T4 GPU + 20 hrs/wk TPU v3-8 (https://www.kaggle.com)"
    },
    "student_edu_perks": {
        "gcp_education_credits": "Up to $500 free semester credits (https://edu.google.com/programs/credits/)",
        "github_student_pack": "Free Azure $100, free JetBrains, free domains (https://education.github.com/pack)",
        "qwiklabs_cloud_skills": "Free hands-on GCP lab sandboxes (https://www.cloudskillsboost.google)"
    }
}

def audit_zero_cost_perks():
    print("========================================================")
    print("  ZERO-COST GCP, .EDU & GOOGLE AI PERKS AUDIT")
    print("========================================================")
    print(f"[+] .EDU Target: {ZERO_COST_RESOURCES['edu_account']}")
    print("\n[1] GOOGLE CLOUD ALWAYS-FREE (NO BILLING / NO CC REQUIRED):")
    for k, v in ZERO_COST_RESOURCES["google_cloud_always_free"].items():
        print(f"  - {k.upper()}: {v}")
        
    print("\n[2] GOOGLE AI & GPU/TPU FREE TIER:")
    for k, v in ZERO_COST_RESOURCES["google_ai_free_tier"].items():
        print(f"  - {k.upper()}: {v}")
        
    print("\n[3] .EDU STUDENT & CAREER LAUNCHPAD PERKS:")
    for k, v in ZERO_COST_RESOURCES["student_edu_perks"].items():
        print(f"  - {k.upper()}: {v}")

    out_file = os.path.join(os.path.dirname(__file__), "..", "data", "zero_cost_gcp_perks.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(ZERO_COST_RESOURCES, f, indent=2)
    print(f"\n[✓] Audit logged to {out_file}")

if __name__ == "__main__":
    audit_zero_cost_perks()
