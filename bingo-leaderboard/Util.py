import requests

def make_request(url, tries=5):
    print(url)
    for i in range(tries):
        response = requests.get(url)
        status = response.status_code

        if status == 200:
            return response.json()
        else:
            print(f'API request failed (status {status} : {response})')