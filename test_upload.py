import requests

url = 'http://134.185.172.127:3011/addService'

data = {
    'user': '{"role":"admin"}',
    'service_id': '10',
    'file_type': 'dictionary'
}

files = {
    'data_file': ('test.csv', 'some,csv,data\n1,2,3', 'text/csv')
}

response = requests.put(url, data=data, files=files)
print(response.status_code)
print(response.text)
