export const encodePassword = (pwd) => {
    if (!pwd) return pwd;
    return '$e$' + btoa(unescape(encodeURIComponent(pwd))).split('').reverse().join('');
};
