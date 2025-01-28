import requests


def query(id):
    url = "http://127.0.0.1:8001/pathways"
    data = {"drugbank_id": id}
    response = requests.post(url, params=data)
    print(response.text)


query("DB01373")
query("DB00001")
query("DB00006")
query("2137")
