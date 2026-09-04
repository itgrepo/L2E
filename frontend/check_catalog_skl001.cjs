const axios = require('axios');
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

fetch('http://134.185.172.127:3003/api/retrieveService', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user: userPayload })
})
  .then(res => res.json())
  .then(res => {
      const data = res.data;
      const found = data.find(d => d.dataset_id === 'SKL-001');
      console.log('SKL-001 in /retrieveService? :', !!found);
  })
  .catch(err => console.error(err.message));
