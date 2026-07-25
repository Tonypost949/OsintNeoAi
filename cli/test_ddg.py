from duckduckgo_search import DDGS

try:
    results = DDGS().chat("hello, who are you?", model='claude-3-haiku')
    print("SUCCESS!")
    print(results)
except Exception as e:
    print("FAILED!")
    print(e)
