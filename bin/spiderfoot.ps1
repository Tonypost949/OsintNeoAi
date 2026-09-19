param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)
& "C:\Users\Amd949609\AppData\Local\Python\pythoncore-3.14-64\python.exe" "C:\spiderfoot\sf.py" @ArgsList
