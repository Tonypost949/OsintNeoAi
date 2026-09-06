const { execFile } = require("child_process");

module.exports.runtime = {
  handler: async function (params = {}) {
    const { query_type, query_text = "", latitude = 0, longitude = 0 } = params;

    try {
      const pythonPath = "C:\\Users\\Amd949609\\AppData\\Local\\Python\\bin\\python.exe";
      const pythonCode = `
import json, os, sys
sys.path.append('C:\\\\OsintNeoAi')
from lightbox_edr_engine import LightBoxEDREngine

engine = LightBoxEDREngine()
q_type = "${query_type}"

if q_type == "search_edr_records":
    res = engine.search_edr_records("${query_text}")
elif q_type == "parcel_by_address":
    res = engine.search_parcel_by_address("${query_text}")
elif q_type == "edr_sites_by_radius":
    res = engine.search_edr_sites_by_radius(${latitude}, ${longitude})
else:
    res = engine.get_summary_stats()

print(json.dumps(res, indent=2))
`;

      const result = await new Promise((resolve, reject) => {
        execFile(pythonPath, ["-c", pythonCode], { cwd: "C:\\OsintNeoAi" }, (error, stdout, stderr) => {
          if (error) return reject(error.message || stderr);
          resolve(stdout);
        });
      });

      return `OsintNeoAi LightBox EDR Engine Output:\n${result}`;
    } catch (err) {
      return `Error executing OsintNeoAi LightBox Engine: ${err.message}`;
    }
  }
};
