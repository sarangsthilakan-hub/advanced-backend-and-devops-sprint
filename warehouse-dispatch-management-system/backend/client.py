from os import access

import requests

API_URL = 'http://127.0.0.1:8001'
user_credentials = {
  "user_name": "Atria3",
  "password": "123456789",
  "user_type": "Admin"
}
login_credentials = {
  "username": "Atria3",
  "password":"123456789"
}

response = requests.post(url= API_URL + "/register",json=user_credentials)
print(response.status_code)
print(response.json())


login_response = requests.post(url= API_URL + "/login",json=login_credentials)
print(login_response.status_code)
print(login_response.json())

response_json = login_response.json()
access_token = response_json['access_token']
refresh_token = response_json['refresh_token']

header = {"token": access_token}
packages_response = requests.get(url=API_URL+"/filtered_packages",headers=header)
print(packages_response.json())

analytics_response = requests.get(url=API_URL+'/warehouse_analytics',headers=header)
print(analytics_response)
print(analytics_response.json())



package_id = 4
delete_res= requests.delete(url=API_URL+'/package/'+f'{package_id}',headers=header)
print(delete_res)
print(delete_res.json())

batch_res= requests.get(url=API_URL+'/dispatch_batches}',headers=header)
print(batch_res)
print(batch_res.json())