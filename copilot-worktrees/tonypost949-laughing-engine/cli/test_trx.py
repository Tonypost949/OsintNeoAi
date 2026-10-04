from core.trx_executor import LocalTRXExecutor

trx = LocalTRXExecutor()
transforms = trx.list_transforms()
print("Transforms:", transforms)

results, err = trx.execute_transform("IPToPorts", "192.168.1.1")
if err:
    print("Error:", err)
else:
    print("Results:", results)
