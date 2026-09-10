const http = require('http');

const payload = {
    user: "eyJ1c2VybmFtZSI6InNzdGkxOTM2NyIsInByZXZpbGFnZV9pZCI6MSwidXNlcl9pZCI6MX0=" // base64 encoded {"username":"ssti19367","previlage_id":1,"user_id":1}
};

const options = {
  hostname: '127.0.0.1',
  port: 3015,
  path: '/getMenuByPermission',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': JSON.stringify(payload).length
  }
};

const req = http.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => {
    console.log('Status:', res.statusCode);
    console.log('Body:', data);
  });
});

req.on('error', (e) => {
  console.error(`Problem: ${e.message}`);
});

req.write(JSON.stringify(payload));
req.end();
