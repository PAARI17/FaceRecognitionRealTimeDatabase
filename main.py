import os
import pickle

import cv2
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("secretkey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-8d0a9-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendancerealtime-8d0a9.appspot.com"
})
bucket=storage.bucket()


#running webcam and graphics
cap=cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

#importing the mode images into a list
imgBackground=cv2.imread('Resources/background.png')
folderModePath='Resources/Modes'
modePath=os.listdir('Resources/Modes')
imgModeList=[]

for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))

#print(len(imgModeList))

#load the encoding file
print("Loading Encode File...")
file =open('EncodeFile.p','rb')
encodeListKnownwithIds=pickle.load(file)
file.close()
encodeListKnown,studentIds=encodeListKnownwithIds
#print(studentIds)
print("Encode FIle Loaded")

modeType=0
counter=0
id=-1
imgStudent=[]

while True:
    success, img=cap.read()
    imgS=cv2.resize(img,(0,0),None,0.25,0.25)
    imgS=cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame=face_recognition.face_locations((imgS))
    encodeCurFrame=face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[162:162+480,55:55+640]=img
    imgBackground[44:44 + 633,808:808 + 414] = imgModeList[modeType]

    for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):
        matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print("matches", matches)
        print("faceDis",faceDis)

        matchindex=np.argmin(faceDis)
        print("Match Index", matchindex)

        if matches[matchindex]:
            #print("Known Face Detected")
            #print(studentIds[matchindex])
            y1,x2,y2,x1=faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            bbox=55+x1,162+y1,x2-x1,y2-y1
            imgBackground=cvzone.cornerRect(imgBackground,bbox,rt=0)
            id = studentIds[matchindex]
            if counter == 0:
                counter=1
                modeType=1
    if counter!=0:
        if counter == 1:
           studentInfo=db.reference(f'Students/{id}').get()
           print(studentInfo)


           blob=bucket.get_blob(f'Images/{id}.png')
           array=np.frombuffer(blob.download_as_string(),np.int8)
           imgStudent=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
           datetimeObject=datetime.strtime(studentInfo['last'])
           ref=db.reference(f'Students/{id}')
           studentInfo['total_attendance']+=1
           ref.child('total_attendance').set(studentInfo['total_attendance'])

        if 10<counter<20:
            modeType=2

        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


        if counter<=10:
            cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),
                        cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)

            cv2.putText(imgBackground, str(studentInfo['Programme']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50,50), 1)
            cv2.putText(imgBackground, str(studentInfo['Roll_No']), (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (50, 50, 50), 1)
            (w,h),_=cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
            offset=(414-w)//2
            cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 455),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 1)
            imgBackground[175:175+216,909:909+216]=imgStudent

        counter +=1

        if counter>=20:
            counter=0
            modeType=0
            studentInfo=[]
            imgStudent=[]
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


    #cv2.imshow("Webcam",img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)

