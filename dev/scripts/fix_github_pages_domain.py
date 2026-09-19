import subprocess
import json

repo = "Tonypost949/OsintNeoAi"
print(f"=== RE-CONFIGURING GITHUB PAGES FOR {repo} ===")

# Clear CNAME and reset Pages configuration
cmd_reset = f'gh api --method PUT -H "Accept: application/vnd.github+json" repos/{repo}/pages -F "cname=" -f "source[branch]=main" -f "source[path]=/docs" 2>&1'
res_reset = subprocess.run(cmd_reset, shell=True, capture_output=True, text=True)

print("Reset Command Output:")
print(res_reset.stdout or res_reset.stderr)

# Request immediate build/deploy
cmd_build = f'gh api --method POST -H "Accept: application/vnd.github+json" repos/{repo}/pages/builds 2>&1'
res_build = subprocess.run(cmd_build, shell=True, capture_output=True, text=True)
print("\nBuild Trigger Output:")
print(res_build.stdout or res_build.stderr)
