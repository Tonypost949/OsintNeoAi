import os

fp = r"C:\Users\HP\Downloads\OSINTNeoAiXXL_chat.json"
if os.path.exists(fp):
    print(f"File exists. Size: {os.path.getsize(fp)}")
    with open(fp, "rb") as f:
        head = f.read(200)
        print("Head (raw):", head)
        try:
            print("Head (decoded utf-8):", head.decode("utf-8"))
        except Exception as e:
            print("Head decode error:", e)
else:
    print("File not found")
