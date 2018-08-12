from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests
import json
import os

scopes = "https://www.googleapis.com/auth/drive"
functionURL = r"https://prod-22.eastasia.logic.azure.com:443/workflows/f18d6c9e410b401e851a2fbdd10aaabb/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=UmjvwpNzBFkWMZW2pJh7CiCNE6Mj0vV-HtIkWSVgkZo"
rootFilePath = "output/"
mapping = {}


def CreateFolders(gooParent, gooId, folderList, service):    
    afFilePath = rootFilePath + "goo/" + gooId + ".json"    
    afList = []
    print("Processing folder {0}...", gooParent)

    for pair in folderList:
        name = pair['name']        
        fileMetadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [gooId]
        }

        newFolder = service.files().create(body=fileMetadata, fields='id').execute()
        afList.append({"name": name, "id": newFolder.get('id')})

    f = open(afFilePath, 'w', encoding='utf-8')
    f.write(json.dumps({"parentFolder": gooParent, "parentFolderId": gooId, "subFolders": afList}))
    f.close()
    print("File {0} is created.", gooId + ".json")

    lenafList = len(afList)
    if lenafList == 0:
        return False    

    for sf in afList:
        CreateFolders(sf['name'], sf['id'], GetFoldersList(rootFilePath + sf['name'] + ".json"), service)

    return True        

def GetFoldersRequest(oneParent, oneId):    
    global functionURL
    subFilePath = rootFilePath + oneId + ".json"

    print("Getting folder {0}...", oneParent)
    if os.path.exists(subFilePath):
        return True

    data = {
        "parentFolder": oneParent, 
        "parentFolderId": oneId }  
            
    dataJson = json.dumps(data, ensure_ascii=False)  

    header = {"content-type": "application/json"}
    response = requests.post(functionURL, data=dataJson.encode('utf-8'), headers=header)
    
    if response.status_code != requests.codes.ok:
        print(response.text)
        return False  
    else:        
        f = open(subFilePath, 'w', encoding='utf-8')        
        f.write(response.text)
        f.close()
        print("File {0} is created.", oneId + ".json")

        fList = GetFoldersList(subFilePath)
        lenfList = len(fList)        

        if lenfList == 0:
            return True
        for sf in fList:
            GetFoldersRequest(sf['name'], sf['id'])
        
        return True

def GetFoldersList(fileName):
    fsFile = open(fileName, 'r', encoding='utf-8')
    fsJson = fsFile.read()
    fsFile.close()

    fsObj = json.loads(fsJson)
    return fsObj['subFolders']

def main():
    # Apply a token thought Oauth.
    store = file.Storage('token.json')
    credit = store.get()

    # Create folders on the Googld Drive.
    if not credit or credit.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', scopes)
        credit = tools.run_flow(flow, store)    
    service = build('drive', 'v3', http = credit.authorize(Http()))    


    # Get sub-folder through Azure logic app.    
    if GetFoldersRequest("11th MSP", "6689F3CBC015F764!165050"):
        # Microsoft student partners id: 1FLs6ehV-TaI45fkjYLkWjq04RdsRIzul        
        CreateFolders("Microsoft Student Partners", "1FLs6ehV-TaI45fkjYLkWjq04RdsRIzul", GetFoldersList(rootFilePath + "Microsoft Student Partners.json"), service)
    
if __name__ == '__main__':
    main()