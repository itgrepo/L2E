const fs = require('fs');
const file = 'frontend/src/components/AppSidebar.vue';
let content = fs.readFileSync(file, 'utf8');

// Fix the onMounted block to not require firstname
content = content.replace(/if \(savedUser\.firstname\) \{/, 'if (savedUser.username) {');
content = content.replace(/userName\.value = `\$\{savedUser\.firstname\}/, 'userName.value = `${savedUser.firstname || savedUser.username}');

fs.writeFileSync(file, content);
