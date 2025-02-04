import os
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("secretkey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-8d0a9-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendancerealtime-8d0a9.appspot.com"
})

# Importing the student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
imgList = []
print(pathList)
studentIds = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    fileName=f'{folderPath}/{path}'
    bucket=storage.bucket()
    blob=bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Corrected this line
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Started")
encodeListKnown = findEncodings(imgList)
encodeListKnownwithIds=[encodeListKnown,studentIds]
print("Encoding Complete")

file=open("EncodeFile.p",'wb')
pickle.dump(encodeListKnownwithIds,file)
file.close()
print("File Saved")