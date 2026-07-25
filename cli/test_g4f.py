import g4f

try:
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[{"role": "user", "content": "Hello"}],
    )
    print("SUCCESS!")
    print(response)
except Exception as e:
    print("FAILED!")
    print(e)
