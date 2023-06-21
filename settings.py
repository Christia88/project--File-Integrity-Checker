import smtplib, ssl
import math
from pathlib import Path
import random
from pymongo import MongoClient
import os
import time
import hashlib
import datetime as datetime


emp_list=[]
os.chdir(r"C:\Users\chris\Pymongo\pymongo_venv")
BLOCK_SIZE = 65536
myclient = MongoClient("mongodb://localhost:27017/")
dbnames = myclient.list_database_names()
mydb = myclient["baselinedb"]
mycole= mydb["email"]
mycol = mydb["baseline"]
mycolp=mydb["password"]
mycols= mydb["settings"]
mycola= mydb["Audit"]

def sha_hash(path,hash_num):
    if hash_num==1:
        f=open(path,'rb')
        fb = f.read(BLOCK_SIZE)
        file_hash = hashlib.sha256()
        while len(fb) > 0: # While there is still data being read from the file
            if type(fb)!=bytes:
                file_hash.update(fb.encode('utf-8')) # Update the hash
                fb = f.read(BLOCK_SIZE) # Read the next block from the file
            else:
                file_hash.update(fb)
                fb=f.read(BLOCK_SIZE)
        hex_hash=file_hash.hexdigest()
        return hex_hash
    elif hash_num==2:
        f=open(path,'rb')
        fb = f.read(BLOCK_SIZE)
        file_hash = hashlib.sha512()
        while len(fb) > 0: # While there is still data being read from the file
            if type(fb)!=bytes:
                file_hash.update(fb.encode('utf-8')) # Update the hash
                fb = f.read(BLOCK_SIZE) # Read the next block from the file
            else:
                file_hash.update(fb)
                fb=f.read(BLOCK_SIZE)
        hex_hash=file_hash.hexdigest()
        return hex_hash
    elif hash_num==3:
        f=open(path,'rb')
        fb = f.read(BLOCK_SIZE)
        file_hash = hashlib.md5()
        while len(fb) > 0: # While there is still data being read from the file
            if type(fb)!=bytes:
                file_hash.update(fb.encode('utf-8')) # Update the hash
                fb = f.read(BLOCK_SIZE) # Read the next block from the file
            else:
                file_hash.update(fb)
                fb=f.read(BLOCK_SIZE)
        hex_hash=file_hash.hexdigest()
        return hex_hash


def check_modify():
    pass_1=0
    k = mycols.find_one({},{'_id': 0, 'hash type': 1})
    hash_num=int(k['hash type'])
    x = mycol.find({},{'_id': 0, 'path': 1,'hash': 1, 'lm': 1})
    for data in x:
        back_path=Path(data["path"])
        temphash=sha_hash(back_path,hash_num)
        ti_m = os.path.getmtime(back_path)
        m_ti = str(time.ctime(ti_m))
        if data["hash"]==temphash:
            pass      # not modified
        elif data["hash"]!=temphash and data["lm"]==m_ti:   # not modified
            pass
        elif data["hash"]!=temphash and data["lm"]!=m_ti: # modified case
            pass_1=1
            print("Cannot continue without authentication")
            break
    return pass_1
    


def Two_step_verify(em):
    ss=0
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "testfic.jabcrypt@gmail.com"
    receiver_email = em
    password = "xrnbwropivwaddbh"
    digit="1234567890"
    OTP=""
    for i in range(4):
        OTP+=digit[math.floor(random.random()*10)]

    message ="Subject: OTP for JABCRYPT: "+OTP

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

    #otp check 
    ot_p=input("OTP has been sent. Enter: ")
    if ot_p==OTP:
        ss=1
    return ss

op1=input("1. Change password \n2. change email\n3. change hash ")
# change password
if op1=="1":
    k = mycole.find_one({},{'_id': 0, 'email': 1})
    em=k["email"]
    ss=Two_step_verify(em)
    if ss==1:
        mycolp.delete_many({}) 
        pas=input("Enter password: ")
        hashed = hashlib.md5(pas.encode())
        hex_hash=hashed.hexdigest()
        passw={ "password": hex_hash }
        x1= mycolp.insert_one(passw)
        cur_time=datetime.now()
        aud_ins={"fname": "none" ,"fpath": "none", "action": "Password Changed","a_time": cur_time,"lm_time": "none"}
        x1= mycola.insert_one(aud_ins)

#change email
elif op1=="2":
    k = mycole.find_one({},{'_id': 0, 'email': 1})
    em=k["email"]
    ss=Two_step_verify(em)
    if ss==1:
        mycole.delete_many({}) 
        pas=input("Enter email: ")
        e_mail={ "email": pas }
        mycole.insert_one(e_mail)
        cur_time=datetime.now()
        aud_ins={"fname": "none" ,"fpath": "none", "action": "Email Changed","a_time": cur_time,"lm_time": "none"}
        x1= mycola.insert_one(aud_ins)

#change hash
elif op1=="3":
    k = mycole.find_one({},{'_id': 0, 'email': 1})
    em=k["email"]
    ss=Two_step_verify(em)
    if ss==1:
        print("change to which hash: \n1. SHA-256 \n2. SHA-512 \n3. MD5")
        ch=input()
        k = mycols.find_one({},{'_id': 0, 'hash type': 1})
        in_p=int(k["hash type"])
        print(in_p)
        if ch==in_p:
            pass
        else:
            kno=check_modify()
            if kno==0:
                print("all files are authenticated")
                mycols.delete_many({}) 
                d_hash={ "hash type": ch }
                mycols.insert_one(d_hash)
                if ch==1:
                    h_string="SHA-256"
                elif ch==2:
                    h_string="SHA-512"
                else:
                    h_string="MD5"
                ch_string="Hash changed to "+h_string
                cur_time=datetime.now()
                aud_ins={"fname": "none" ,"fpath": "none", "action": ch_string,"a_time": cur_time,"lm_time": "none"}
                x1= mycola.insert_one(aud_ins)
                print(ch)

                ko = mycols.find_one({},{'_id': 0, 'hash type': 1})
                hash_num=int(ko['hash type'])
                print(hash_num)
                x = mycol.find({},{'_id': 0, 'path': 1,'hash': 1, 'lm': 1})
                for data in x:
                    b_path=Path(data["path"])
                    hash1=sha_hash(b_path,hash_num)
                    myquery = { "path": data["path"] }
                    newvalues = { "$set": { "hash": hash1 } }
                    print(hash1)
                    mycol.update_one(myquery, newvalues)
