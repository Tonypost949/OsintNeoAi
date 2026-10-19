import subprocess

cmd1 = 'az webapp config set --name osintneoai-webapp --resource-group osintneoai-rg --linux-fx-version "PYTHON|3.9" --startup-file "gunicorn app:app"'
res1 = subprocess.run(cmd1, shell=True, capture_output=True, text=True)

print("=== RESETTING AZURE RUNTIME TO PYTHON 3.9 (gunicorn app:app) ===")
print("Output:", res1.stdout or res1.stderr)

cmd2 = 'az webapp restart --name osintneoai-webapp --resource-group osintneoai-rg'
res2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
print("Restart Output:", res2.stdout or res2.stderr)
