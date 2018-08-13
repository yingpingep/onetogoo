import requests
import json

def main():
    url = r"https://prod-00.eastasia.logic.azure.com:443/workflows/b45257f6b94a486a853ac2c04b2fc4e3/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YCMVuowoHKv_baRt1mlU9qFgA9I5r472PziFfredtoE"

    data = {
        "gooParentPath": "/Microsoft Student Partners",
        "oneParentId": "6689F3CBC015F764!194645"
    }

    dataJson = json.dumps(data, ensure_ascii=False)
    res = requests.post(url, data=dataJson.encode('utf-8'), headers={"content-type": "application/json"})

    print(res.status_code)

if __name__ == '__main__':
    main()