const userPermissions = ['dashboard', 'catalog'];

const menuMapping = {
    '/dashboard': 'dashboard',
    '/catalog': 'catalog',
    '/api-management': 'api management'
};

function hasMenuAccess(path) {
    const mappedName = menuMapping[path];
    if (mappedName) {
        if (mappedName === 'catalog') {
            return userPermissions.includes('catalog') || userPermissions.includes('data catalog');
        }
        return userPermissions.includes(mappedName);
    }
    return false;
}

console.log('/dashboard', hasMenuAccess('/dashboard'));
console.log('/catalog', hasMenuAccess('/catalog'));
