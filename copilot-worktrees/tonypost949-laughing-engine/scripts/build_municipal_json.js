const fs = require('fs');

function parseCSV(filePath) {
  const text = fs.readFileSync(filePath, 'utf8');
  const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);
  if (lines.length === 0) return [];
  
  function parseLine(line) {
    const row = [];
    let inQuote = false;
    let token = '';
    for (let j = 0; j < line.length; j++) {
      const c = line[j];
      if (c === '"') {
        inQuote = !inQuote;
      } else if (c === ',' && !inQuote) {
        row.push(token.trim().replace(/^"|"$/g, ''));
        token = '';
      } else {
        token += c;
      }
    }
    row.push(token.trim().replace(/^"|"$/g, ''));
    return row;
  }

  const headers = parseLine(lines[0]);
  const records = [];

  for (let i = 1; i < lines.length; i++) {
    const row = parseLine(lines[i]);
    if (row.length > 0) {
      const obj = {};
      headers.forEach((h, idx) => {
        obj[h] = row[idx] || '';
      });
      records.push(obj);
    }
  }
  return records;
}

if (!fs.existsSync('public/data')) {
  fs.mkdirSync('public/data', { recursive: true });
}

const matrix = parseCSV('reports/ALL_REPO_CITIES_DATA_SYSTEMS_IRC_MATRIX.csv');
fs.writeFileSync('public/data/municipal_matrix.json', JSON.stringify(matrix, null, 2));

const ips = parseCSV('reports/ALL_REPO_CITIES_AND_IPS_NETWORK_MATRIX.csv');
fs.writeFileSync('public/data/cities_ips.json', JSON.stringify(ips, null, 2));

console.log(`Generated public/data/municipal_matrix.json (${matrix.length} records) and public/data/cities_ips.json (${ips.length} records).`);
