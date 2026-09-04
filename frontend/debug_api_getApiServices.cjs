const btoa = (str) => Buffer.from(str).toString('base64');
const userPayload = btoa(unescape(encodeURIComponent(JSON.stringify({
    user_id: 1,
    username: 'admin',
    role_id: 3,
    previlage_id: 3,
    isAdmin: 'true',
    firstname: 'Admin',
    apikey: 'mock_key'
}))));

fetch('http://134.185.172.127:3003/api/getApiServices', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user: userPayload })
})
  .then(res => res.json())
  .then(res => console.log(res))
  .catch(err => console.error(err.message));
