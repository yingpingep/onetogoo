from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests

scopes = "https://www.googleapis.com/auth/drive"
functionURL = r"https://prod-22.eastasia.logic.azure.com:443/workflows/f18d6c9e410b401e851a2fbdd10aaabb/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=UmjvwpNzBFkWMZW2pJh7CiCNE6Mj0vV-HtIkWSVgkZo"
folderNames = []

def CreateFolder(name, parents, service):
    fileMetadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': parents
    }

    newFile = service.files().create(body=fileMetadata, fields='id').execute()
    print('Folder ID:', newFile.get('id')) 

def MakeRequest(folderName):
    global functionURL
    data = {"folder": folderName}
    response = requests.post(functionURL, data = data, headers={"Content-Type": "application/json"})
    print(response.text)

def main():
    # Apply a token thought Oauth.
    # store = file.Storage('token.json')
    # credit = store.get()
    # if not credit or credit.invalid:
    #     flow = client.flow_from_clientsecrets('credentials.json', scopes)
    #     credit = tools.run_flow(flow, store)    
    # service = build('drive', 'v3', http = credit.authorize(Http()))    

    MakeRequest('tet')

if __name__ == '__main__':
    main()