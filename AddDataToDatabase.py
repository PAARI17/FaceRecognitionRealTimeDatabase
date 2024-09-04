import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("secretkey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-8d0a9-default-rtdb.firebaseio.com/"
})

ref =db.reference('Students')

data={
    "45":
        {
            "name":"Paritosh Sabarad",
            "Programme":"B.Tech C.E",
            "Roll_No":"45",
            "total_attendance":10

        },
"46":
        {
            "name":"Shahrukh Khan",
            "Programme":"B.Tech C.E",
            "Roll_No":"46",
            "total_attendance":12
        }
}

for key,value in data.items():
    ref.child(key).set(value)


