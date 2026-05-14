const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'frontend', 'src');

const replacements = [
  { regex: /#ba1a5d/gi, replacement: 'var(--primary)' },
  { regex: /#9d0d4e/gi, replacement: 'var(--primary-hover)' },
  { regex: /#e91e63/gi, replacement: 'var(--mso-accent)' },
  { regex: /#ec4899/gi, replacement: 'var(--mso-accent)' },
  // Also replace some tailwind classes where possible, or specific inline stuff.
  // We'll focus on the hex codes first.
];

function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      processDirectory(fullPath);
    } else if (file.endsWith('.vue') || file.endsWith('.css')) {
      let content = fs.readFileSync(fullPath, 'utf8');
      let changed = false;
      for (const r of replacements) {
        if (r.regex.test(content)) {
          content = content.replace(r.regex, r.replacement);
          changed = true;
        }
      }
      if (changed) {
        fs.writeFileSync(fullPath, content, 'utf8');
        console.log(`Updated: ${fullPath}`);
      }
    }
  }
}

processDirectory(srcDir);
