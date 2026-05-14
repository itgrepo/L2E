const fs = require('fs');
const path = require('path');

const srcDir = path.join(__dirname, 'frontend', 'src');

const replacements = [
  { regex: /\bbg-pink-600\b/g, replacement: 'bg-[var(--primary)]' },
  { regex: /\btext-pink-600\b/g, replacement: 'text-[var(--primary)]' },
  { regex: /\btext-pink-400\b/g, replacement: 'text-[var(--primary)]' },
  { regex: /\bfrom-pink-600\b/g, replacement: 'from-[var(--primary)]' },
  { regex: /\bto-pink-800\b/g, replacement: 'to-[var(--primary-hover)]' }
];

function processDirectory(dir) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      processDirectory(fullPath);
    } else if (file.endsWith('.vue')) {
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
        console.log(`Updated Tailwind: ${fullPath}`);
      }
    }
  }
}

processDirectory(srcDir);
