const userData = {
  user_id: 1,
  username: 'admin',
  role: 'System Administrator'
};
const jsonStr = JSON.stringify(userData);
const b64 = Buffer.from(jsonStr).toString('base64');
const reversed = b64.split('').reverse().join('');
const randomChars = 'abcde';
console.log(reversed + randomChars);
