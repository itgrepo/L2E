const fs = require('fs');
const file = 'frontend/src/router/index.js';
let content = fs.readFileSync(file, 'utf8');

const newRoute = `
    {
      path: '/unlock/:token',
      name: 'unlock-account',
      component: () => import('../views/UnlockAccountView.vue')
    },`;

if (!content.includes('/unlock/:token')) {
    content = content.replace("routes: [", "routes: [" + newRoute);
    fs.writeFileSync(file, content);
    console.log("Patched router");
} else {
    console.log("Already patched");
}
