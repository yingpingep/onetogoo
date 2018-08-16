from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from folder import *
import requests
import json
import os
import sys

scopes = "https://www.googleapis.com/auth/drive"
getFileUrl = r""
movingUrl = r""

rootFilePath = "output/"
outputFile = rootFilePath + "mapping.json"
mapping = {}

def GetUrlSetting():
    global getFileUrl, movingUrl'
    fileName = "logicsetting.json"
    if os.path.exists(fileName):
        print("Cannot find Logic app setting file: {0}.".format(fileName))
        sys.exit()

    f = open(fileName, "r", encoding="utf-8")
    setting = json.loads(f.read())
    f.close()
    getFileUrl = setting["getFileUrl"]
    movingUrl = setting["movingUrl"]

    return True

def MovingFiles(dir):
    print("Moving files in folder {0}...".format(dir.name), end="\t")
    correctPath = dir.GetPath() + dir.name
    data = {
        "path": correctPath,
        "oneId": dir.oneId
    }

    dataJson = json.dumps(data, ensure_ascii=False)
    response = requests.post(movingUrl, data=dataJson.encode('utf-8'), headers={"content-type": "application/json"})    

    if response.status_code != requests.codes.ok:
        print("\n" + response.text)
    else:
        print("DONE.")

    for sub in dir.children:
        key = sub["oneId"]
        try:
            mapping[key]
        except KeyError:
            OutOfMapping(sub["oneId"], correctPath + "/" + sub["name"], sub["name"])
        else:
            MovingFiles(mapping[key])

def OutOfMapping(oneId, path, name):
    print("Moving files in {0}...".format(name), end="\t")
    data = {
        "path": path,
        "oneId": oneId
    }

    dataJson = json.dumps(data, ensure_ascii=False)
    response = requests.post(movingUrl, data=dataJson.encode('utf-8'), headers={"content-type": "application/json"})    

    if response.status_code != requests.codes.ok:
        print("\n" + response.text)
    else:
        print("DONE.")

def CreateFolders(dir, service):
    print("Processing folder {0}...".format(dir.name))

    if len(dir.children) == 0:
        return

    for sub in dir.children:
        fileMetadata = {
            "name": sub["name"],
            "mimeType": "application/vnd.google-apps.folder",
            'parents': [dir.gooId]
        }

        newFolder = service.files().create(body=fileMetadata, fields="id").execute()
        key = sub["oneId"]

        try:
            mapping[key]
        except KeyError:
            pass
        else:
            mapping[key].gooId = newFolder.get("id")
            CreateFolders(mapping[key], service)
        
    return

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
            return True

        dir.children = sub                   

        for sf in dir.children:
            temp = Folder(sf["name"], sf["oneId"])
            temp.parents = dir.parents.copy()
            temp.parents.append(dir.name)          
            GetFolders(temp)
        return True

def Usage():
    sys.exit()

def main():    
    global mapping
    
    # Make sure there is a folder named "output".
    if not os.path.exists(rootFilePath):
        os.makedirs("output")

    # Apply a token thought Oauth.
    store = file.Storage('token.json')
    credit = store.get()

    # Create folders on the Googld Drive.
    if not credit or credit.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', scopes)
        credit = tools.run_flow(flow, store)    
    service = build('drive', 'v3', http = credit.authorize(Http()))        

    # root = Folder("Microsoft Student Partners", "6689F3CBC015F764!234053", "1FLs6ehV-TaI45fkjYLkWjq04RdsRIzul")   
    # if not os.path.exists(outputFile):             
    #     GetFolders(root)
    #     f = open(outputFile, "w", encoding="utf-8")
    #     f.write(Folder.Encoder(mapping))
    #     f.close()
    # else:
    #     f = open(outputFile, "r", encoding="utf-8")
    #     text = f.read()
    #     mapping = Folder.Decoder(text)
    # CreateFolders(mapping[root.oneId], service)    
    
if __name__ == '__main__':
    if len(sys.argv) < 1:
        Usage()

    for arg in range(0, len(sys.argv)):
        pass

    main()