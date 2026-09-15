const fs = require('fs');
const path = require('path');

for (const name of ['capture.cjs', 'capture-1920.cjs']) {
  const file = path.join(__dirname, name);
  const source = fs.readFileSync(file, 'utf8').replace(/^\+/gm, '');
  fs.writeFileSync(file, source);
}

console.log('Removed accidental diff markers from both capture scripts.');
