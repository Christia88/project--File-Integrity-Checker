from pymongo import MongoClient
from datetime import datetime
from pathlib import Path
import hashlib
import os.path 
import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

emp_list=[]
os.chdir(r"C:\Users\chris\Pymongo\pymongo_venv")
BLOCK_SIZE = 65536
myclient = MongoClient("mongodb://localhost:27017/")
p=Path(r"C:\Users\chris\OneDrive\Desktop\hello")
dbnames = myclient.list_database_names()
new_list=[]
mod_file=[]

file_path=[]
dir_path=[]
files_tot=[]
for ij in p.glob('*'):
    files_tot.append(str(ij))
for b in files_tot:
    if os.path.isfile(b)==True:
        file_path.append(b)
    elif os.path.isdir(b)==True:
        dir_path.append(b)
print(file_path)
print(dir_path)
files_tot=[]

if dir_path!=emp_list:
    while dir_path!=emp_list:
        for dir1 in dir_path:
            p=Path(dir1)
            for ij in p.glob('*'):
                b=str(ij)
                if os.path.isfile(b)==True:
                    file_path.append(b)
                elif os.path.isdir(b)==True:
                    dir_path.append(b)
            dir_path.remove(dir1)

new_path=[]
for path_temp in file_path:
    new_path.append(Path(path_temp))


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

        
#if database does not exists

if 'baselinedb' not in dbnames:   
    mydb = myclient["baselinedb"]
    mycol = mydb["baseline"]
    mycolp= mydb["password"]
    mycols= mydb["settings"]
    mycole= mydb["email"]
    mycola= mydb["Audit"]


    # to enter password
    pas=input("Enter password: ")
    hashed = hashlib.md5(pas.encode())
    hex_hash=hashed.hexdigest()
    passw={ "password": hex_hash }
    x1= mycolp.insert_one(passw)

    #enter email
    em=input("enter email: ")
    e_mail={ "email": em }
    x1= mycole.insert_one(e_mail)

    #default hash
    hash_t={ "hash type": 1 }
    x1= mycols.insert_one(hash_t)

    # authenticate google drive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    gauth.SaveCredentialsFile("mycreds.txt")

    k = mycols.find_one({},{'_id': 0, 'hash type': 1})
    hash_num=int(k["hash type"])
    for path in new_path:
        has_h=sha_hash(path,hash_num)
        ti_m = os.path.getmtime(path)
        m_ti = str(time.ctime(ti_m))
        mydict = { "path":str(path), "hash": has_h, "lm": m_ti }
        x = mycol.insert_one(mydict)
        cur_time=datetime.now()
        file_name = os.path.basename(path)
        aud_ins={"fname": str(file_name) ,"fpath": str(path), "action": "Newly Scanned","a_time": cur_time,"lm_time": m_ti}
        x1= mycola.insert_one(aud_ins)

        # to upload files to the google drive
        pat_h=str(path)
        f = drive.CreateFile({'title': pat_h })
        f.SetContentFile(pat_h)
        f.Upload()
        f = None

#if database exists

elif 'baselinedb' in dbnames:    
    mydb = myclient["baselinedb"]
    mycol = mydb["baseline"]
    mycolp=mydb["password"]
    mycols= mydb["settings"]
    mycola= mydb["Audit"]

    for path in new_path:
        x = mycol.find({},{'_id': 0, 'path': 1,'hash': 1, 'lm': 1})
        for data in x:
            if data["path"]==str(path):
                k = mycols.find_one({},{'_id': 0, 'hash type': 1})
                hash_num=int(k['hash type'])
                temphash=sha_hash(path,hash_num)
                ti_m = os.path.getmtime(path)
                m_ti = str(time.ctime(ti_m))
                if data["hash"]==temphash:
                    print("not modified:",path)         # not modified
                elif data["hash"]!=temphash and data["lm"]==m_ti:   # not modified
                    print("not modified:",path)
                elif data["hash"]!=temphash and data["lm"]!=m_ti:    # modified case
                    cur = str(datetime.now())
                    curt=cur.split()
                    cur=curt[1]
                    timn=cur.split(".")
                    timn=timn[0]
                    r1=curt[0]
                    r1=r1.split("-")
                    res= m_ti.split()
                    timb=res[3]
                    bef_t=""
                    cur_t1=""
                    mons=["0","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
                    mn=res[1]
                    do=res[2]
                    y=res[4]
                    for i in mons:
                        if i==mn:
                            a=str(mons.index(i))
                    bef_t=do+"/"+a+"/"+y
                    cur_t=r1[2]+"/"+r1[1]+"/"+r1[0]
                    dat1 = datetime.strptime(bef_t, "%d/%m/%Y")
                    dat2 = datetime.strptime(cur_t, "%d/%m/%Y")
                    diff_dat=str(dat2-dat1)
                    diff_dat=diff_dat.split(", ")
                    diff_dat=diff_dat[0]
                        
                    print("\nfile modified:       ",path)
                    mod_file.append(path)
                    cur_time=datetime.now()
                    file_name = os.path.basename(path)
                    aud_ins={"fname": str(file_name) ,"fpath": str(path), "action": "Modified","a_time": cur_time,"lm_time": m_ti}
                    x1= mycola.insert_one(aud_ins)

                    if diff_dat=="0:00:00":
                        start = datetime.strptime(timb, "%H:%M:%S")
                        end = datetime.strptime(timn, "%H:%M:%S")
                        diff_time = end - start
                        diff_time=str(diff_time)
                        diff_time=diff_time.split(":")
                        hrs = diff_time[0]
                        mins=diff_time[1]
                        second=diff_time[2]
                        print(f"Modified today at {timb}, {hrs} hours, {mins} minutes and {second} seconds ago.\n")
                    else:
                        print(f"Modified {diff_dat} ago at {timb}.\n")
                            
            
            else:
                continue

    # scan for new files to put into baseline database
    x.close()
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    gauth.LoadCredentialsFile("mycreds.txt")

    for path in new_path:
        count=0
        q = mycol.find({},{'_id': 0, 'path': 1})
        for o in q:
            if o["path"]==str(path):
                count=1
            else:
                continue
        if count==0:
            print("new file added: ",str(path))
            k = mycols.find_one({},{'_id': 0, 'hash type': 1})
            hash_num=int(k["hash type"])
            has_h=sha_hash(path,hash_num)
            ti_m = os.path.getmtime(path)
            m_ti = str(time.ctime(ti_m))
            mydict = { "path":str(path), "hash": has_h, "lm": m_ti }
            x = mycol.insert_one(mydict)
            cur_time=datetime.now()
            file_name = os.path.basename(path)
            aud_ins={"fname": str(file_name) ,"fpath": str(path), "action": "Newly Scanned","a_time": cur_time,"lm_time": m_ti}
            x1= mycola.insert_one(aud_ins)

            # TO INSERT NEW FILES INTO THE GOOGLE DRIVE

            pat_h=str(path)
            f = drive.CreateFile({'title': pat_h })
            f.SetContentFile(pat_h)
            f.Upload()
            f = None

    au_list=[]
    re_list=[]
    file_list = drive.ListFile({'q': 'trashed=false'}).GetList()
    for file in file_list:
        new_l={"title":file['title'],"id": file['id']}
        new_list.append(new_l)
    # to authenticate modification
    for path in mod_file:
        print("\nfile modified:   ",path)
        print("Authenticate changes / revert file / none <a/r/n> : ",end="") 
        ch=input()
        if ch=="a":
            au_list.append(path)
        elif ch=="r":
            re_list.append(path)
        else:
            continue
    
    if au_list!=emp_list:
        temp_pass=input("enter password: ")
        hashed = hashlib.md5(temp_pass.encode())
        hex_hash=hashed.hexdigest()
        k = mycolp.find_one({},{'_id': 0, 'password': 1})
        if k["password"]==hex_hash:
            for path in au_list:
                del_d={"path": str(path) }
                mycol.delete_one(del_d)
                ti_m = os.path.getmtime(path)
                m_ti = str(time.ctime(ti_m))
                k = mycols.find_one({},{'_id': 0, 'hash type': 1})
                hash_num=int(k["hash type"])
                has_h=sha_hash(path,hash_num) 
                mydict = { "path":str(path), "hash": temphash, "lm": m_ti }
                x = mycol.insert_one(mydict)
                cur_time=datetime.now()
                file_name = os.path.basename(path)
                aud_ins={"fname": str(file_name) ,"fpath": str(path), "action": "Authenticated","a_time": cur_time,"lm_time": m_ti}
                x1= mycola.insert_one(aud_ins)
                #deleting file in google drive and adding the new one
                for i in new_list:
                    s_path=str(path)
                    i_path=str(i["title"])
                    if s_path==i_path:
                        a=i["id"]
                        file = drive.CreateFile({'id': a})
                        file.Trash()

                pat_h=str(path)
                f = drive.CreateFile({'title': pat_h })
                f.SetContentFile(pat_h)
                f.Upload()
                f = None
            au_list=[]    

    if re_list!=emp_list:
        temp_pass=input("enter password: ")
        hashed = hashlib.md5(temp_pass.encode())
        hex_hash=hashed.hexdigest()
        k = mycolp.find_one({},{'_id': 0, 'password': 1})
        if k["password"]==hex_hash:
            for path in re_list:
                for i in new_list:
                    s_path=str(path)
                    i_path=str(i["title"])
                    if s_path==i_path:
                        file = drive.CreateFile({'id': i["id"]})
                        file.GetContentFile(s_path)
                        cur_time=datetime.now()
                        file_name = os.path.basename(path)
                        aud_ins={"fname": str(file_name) ,"fpath": str(s_path), "action": "Reverted","a_time": cur_time,"lm_time": m_ti}
                        x1= mycola.insert_one(aud_ins)
            re_list=[]
