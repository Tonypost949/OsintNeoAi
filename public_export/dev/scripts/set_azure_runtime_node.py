import subprocess

cmd = 'az webapp config set --name osintneoai-webapp --resource-group osintneoai-rg --linux-fx-version "NODE|18-lts" --startup-file "npx -y serve -s -p 8080 ."'
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

print("=== SET AZURE RUNTIME TO NODE 18 & NPX SERVE ===")
print("Return Code:", res.returncode)
print("Output:", res.stdout)
print("Error:", res.stderr)

res2 = subprocess.run('az webapp restart --name osintneoai-webapp --resource-group osintneoai-rg', shell=True, capture_output=True, text=True)
print("\nRestarted Web App!")
