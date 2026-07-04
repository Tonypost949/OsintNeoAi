from core.trx_executor import LocalTRXExecutor

trx = LocalTRXExecutor()
results, err = trx.execute_transform("WebSearch", "HBNC")

if err:
    print("Error:", err)
else:
    print("Results:", results)
