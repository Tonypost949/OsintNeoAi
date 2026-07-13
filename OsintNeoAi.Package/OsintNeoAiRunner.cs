using System;
using System.Diagnostics;
using System.IO;

namespace OsintNeoAi
{
    public static class OsintNeoAiRunner
    {
        public static Process RunCli(string pythonPath, string workingDir, string args = "")
        {
            var mainScript = Path.Combine(workingDir, "OsintNeoAi", "main.py");
            if (!File.Exists(mainScript))
            {
                // Fallback to checking standard relative path
                mainScript = Path.Combine(workingDir, "main.py");
            }

            var startInfo = new ProcessStartInfo
            {
                FileName = pythonPath,
                Arguments = $"\"{mainScript}\" cli {args}",
                WorkingDirectory = workingDir,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            return Process.Start(startInfo);
        }
    }
}
