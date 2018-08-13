from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from folder import *
import requests
import json
import os

scopes = "https://www.googleapis.com/auth/drive"
getFileUrl = r"https://prod-22.eastasia.logic.azure.com:443/workflows/f18d6c9e410b401e851a2fbdd10aaabb/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=UmjvwpNzBFkWMZW2pJh7CiCNE6Mj0vV-HtIkWSVgkZo"
movingUrl = r"https://prod-00.eastasia.logic.azure.com:443/workflows/b45257f6b94a486a853ac2c04b2fc4e3/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YCMVuowoHKv_baRt1mlU9qFgA9I5r472PziFfredtoE"

gooRootPath = "/Microsoft Student Partners"
rootFilePath = "output/"
mapping = {}

def CreateFolders(dir):
    print("Processing folder {0}...", dir.name)

    if len(dir.children) == 0:
        return True

    for sub in dir.children:
        fileMetadata = {
            "name": sub["name"],
            "mimeType": "application/vnd.google-apps.folder",
            'parents': [dir.gooId]
        }

        newFolder = service.files().create(body=fileMetadata, fields="id").execute()

        try:
            mapping[sub["name"]]
        except KeyError:
            pass
        else:
            mapping[sub].gooId = newFolder.get("id")
            CreateFolders(mapping[sub["name"]])
        
    return True


def O_CreateFolders(gooParent, gooId, folderList, service):    
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
        O_CreateFolders(sf['name'], sf['id'], O_GetFoldersList(rootFilePath + sf['name'] + ".json"), service)

    return True        

def GetFolders(dir):
    oid = dir.oneId
    data = {"oneId": oid}
    dataJson = json.dumps(data)
    header = {"content-type": "application/json"}
    response = requests.post(getFileUrl, data=dataJson.encode('utf-8'), headers=header)

    if response.status_code != requests.codes.ok:
        print(response.text)
        return False
    else:
        resJson = json.loads(response.text)
        sub = resJson["subFolders"]
        print("{0} with {1} sub-folders is recoded.".format(dir.name, len(sub)))

        if len(sub) == 0:            
            return False

        dir.children = sub
        mapping[dir.name] = dir            

        for sf in dir.children:
            temp = Folder(sf["name"], sf["oneId"])
            temp.parents = dir.parents.copy()
            temp.parents.append(dir.name)          
            GetFolders(temp)
        return True

def main():
    # Apply a token thought Oauth.
    store = file.Storage('token.json')
    credit = store.get()

    # Create folders on the Googld Drive.
    if not credit or credit.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', scopes)
        credit = tools.run_flow(flow, store)    
    service = build('drive', 'v3', http = credit.authorize(Http()))    

    root = Folder("Microsoft Student Partners", "6689F3CBC015F764!234053", "1FLs6ehV-TaI45fkjYLkWjq04RdsRIzul")        
    GetFolders(root)
    f = open(rootFilePath + "mapping.json", "w", encoding="utf-8")
    f.write(json.dumps(mapping, cls=FolderConvert, sort_keys=True, indent=4))
    f.close()
    CreateFolders(mapping[root.name])    

    # Get sub-folder through Azure logic app.    
    # if O_GetFoldersRequest("11th MSP", "6689F3CBC015F764!165050"):
    #     # Microsoft student partners id: 1FLs6ehV-TaI45fkjYLkWjq04RdsRIzul        
    #     O_CreateFolders("Microsoft Student Partners", "1FLs6ehV-TaI45fkjYLkWjq04RdsRIzul", O_GetFoldersList(rootFilePath + "Microsoft Student Partners.json"), service)
    
if __name__ == '__main__':
    main()