# 用法參考https://geocoder.readthedocs.io/
import requests
url = 'https://maps.googleapis.com/maps/api/geocode/json'
params = {'key': 'your key', 'address': '新竹市東區大學路1001號'}
r = requests.get(url, params=params)
results = r.json()['results']
location = results[0]['geometry']['location']
print(location['lat'])
print(location['lng'])