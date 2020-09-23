import requests

url = "https://gorest.co.in/public-api/users"

payload = {}
headers = {
  'Cookie': '_gorest_session=r%2BBvzjOXrd%2Bnzm7PZAmgk8uHL0zBgVzTiSHjHeAMW7lCeQbnougpAJj7DFW4tRru%2BZxMF%2BgfnpmDA2aAAfms%2Fc5rDrD4h77iUNT1FKHIm3GyyttPrb41IzA9sckwd2KGbGH2%2BcD%2FCl1BIcCkAhRrL6yFxBIkl7T%2BPxsv0KEwTcz31m46uMY1OEuUC5rYvR2laiYDkIcqtlkCySMruCcj9ZjMvE%2BICL7N5Bpagl1XhKwTDDW0GfLcVmKKcBNNbJmtw%2FP1OqwKjcXtodeHWQQZuPZTgBR%2BmIA%3D--e%2BQr73izlCmBWSy2--yOmZzROPWDzaOBb6fUT24A%3D%3D'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))
# response = requests.get('https://gorest.co.in/public-api/users')
# print(response.text)

# convert json to Python object 
x = response.json()

# print(type(x)) # dict

# print(x['data'][0]['name'])
# print(x['data'][1]['name'])

values = x['data']
# print(type(values)) # List

for n in range(len(values)):
  print(values[n]['name'])