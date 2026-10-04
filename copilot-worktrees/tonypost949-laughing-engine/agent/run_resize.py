import subprocess
import base64

# PowerShell commands to delete partition F and expand C
ps_command = (
    "Remove-Partition -DriveLetter F -Confirm:$false; "
    "Resize-Partition -DriveLetter C -Size (Get-PartitionSupportedSize -DriveLetter C).SizeMax"
)

# Encode to UTF-16LE and Base64 as required by PowerShell -EncodedCommand
encoded_command = base64.b64encode(ps_command.encode("utf-16-le")).decode("ascii")

# Run via Start-Process with RunAs verb to trigger UAC elevation
run_command = f"Start-Process powershell -ArgumentList '-NoProfile -EncodedCommand {encoded_command}' -Verb RunAs"

print(f"Executing elevated command...")
subprocess.run(["powershell", "-NoProfile", "-Command", run_command])
print("Resizing request sent to system.")
