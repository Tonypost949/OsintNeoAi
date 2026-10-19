from core.trx_executor import LocalTRXExecutor

trx = LocalTRXExecutor()
transforms = trx.list_transforms()
print("Transforms:", transforms)

results, err = trx.execute_transform("IPToPorts", "[PRIVATE_IP]")
if err:
    print("Error:", err)
else:
    print("Results:", results)
