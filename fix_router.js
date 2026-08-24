const fs = require('fs');
const routerFile = 'frontend/src/router/index.js';
let content = fs.readFileSync(routerFile, 'utf8');

const adminRoutes = [
  'dashboard',
  'api-management',
  'api-monitor',
  'user-management',
  'permission-management',
  'group-user-management',
  'dataset-management',
  'group-dataset-management',
  'dataset-permission-monitor',
  'organization-management',
  'category-management'
];

adminRoutes.forEach(route => {
  const regex = new RegExp(`name:\\s*'${route}',\\s*component:[\\s\\S]*?meta:\\s*{([^}]+)}`, 'g');
  content = content.replace(regex, (match, metaContent) => {
    if (!metaContent.includes('requiresAdmin')) {
      return match.replace(metaContent, metaContent + ', requiresAdmin: true');
    }
    return match;
  });
  
  const regexNoMeta = new RegExp(`name:\\s*'${route}',\\s*component:\\s*\\(\\)\\s*=>\\s*import\\([^)]+\\)\\s*\\}`, 'g');
  content = content.replace(regexNoMeta, (match) => {
    return match.replace('}', ',\n      meta: { requiresAuth: true, requiresAdmin: true }\n    }');
  });
});

const newGuard = `// Navigation Guard
router.beforeEach((to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null');
  
  if (to.meta.requiresAuth && !user) {
    next({ name: 'login' });
  } else if (to.meta.requiresAdmin && user) {
    // Check if user is admin
    const isAdmin = user.isAdmin === 'true' || user.isAdmin === true || ['3', '4'].includes(String(user.role_id));
    if (!isAdmin) {
      next({ name: 'home' }); // Redirect to home if not admin
    } else {
      next();
    }
  } else {
    next();
  }
});`;

content = content.replace(/\/\/ Navigation Guard[\s\S]*?export default router/, newGuard + '\n\nexport default router');

fs.writeFileSync(routerFile, content);
console.log("Router updated successfully.");
