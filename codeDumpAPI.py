from asyncio import tasks
from dataclasses import field
import threading
import time
from flask import Flask,jsonify,request,make_response
from configparser import ConfigParser
import zipfile
import os
import sys
from datetime import datetime
from flask_cors import CORS
import json
import shutil
import pymysql
from pathlib import Path
import multiprocessing

import subprocess

file='config.ini'
config= ConfigParser()
config.read(file)

print(config.sections())

app=Flask(__name__)

CORS(app)

with open("configfile.json", 'r') as f:
  configfile = json.load(f)
  


@app.route('/api',methods=['POST'])
def recieveZip():
    conn = pymysql.connect(
        host = '159.89.168.228',
        user = 'root',
        password = 'prod',
        db='DevopsAdmin'
        
    )
    try:
        APPNAME=''
        flag=True
        responseMessage=''
        file = request.data
        for headerKeyPair in request.headers:
             header=list(headerKeyPair)
             print(header)
             if "Appname" in header:
                APPNAME=header[1]
                break

        cur = conn.cursor(pymysql.cursors.DictCursor)
        result= cur.execute("SELECT project_name FROM project_details WHERE project_id=%s",(APPNAME,))
        if(result>=1):
            output = cur.fetchall()
            cur.close()
            print(output)   
        project=output[0]["project_name"]    
        path=config[project]['path']
        curDT = datetime.now()
        now=curDT.strftime('%Y%m%d%H%M%S')
        fullZipPath=os.path.join(path, f"my_file{now}.zip")
        with open(fullZipPath, "wb") as binary_file:
            binary_file.write(file)
        with zipfile.ZipFile(fullZipPath, 'r') as zip_ref:
            zip_ref.extractall(path)
        os.remove(fullZipPath)
    except Exception as e:
        #responseMessage = sys.exc_info()[0]
        print(sys.exc_info()[0])
        responseMessage = "error occured"
        print(e)
        flag=False
    finally:
        if flag:
             positiveData = {'message': 'Done', 'code': 'Uploaded successfully'}
             return make_response(jsonify(positiveData), 200)
        else:
             negativeData = {'message': responseMessage, 'code': 'Failed!'}
             return make_response(jsonify(negativeData), 200)
             

             
@app.route('/migrate',methods=['POST'])
def CopyToTarget():
    conn = pymysql.connect(
        host = '159.89.168.228',
        user = 'root',
        password = 'prod',
        db='DevopsAdmin'
        
    )
    flag=True
   
    fileid = request.json['fileid']
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        result= cur.execute("SELECT p.volume_path,p.containername,p.project_name FROM project_details p, filedetails f WHERE f.id=%s AND p.project_id=f.project_id",(fileid,))
        
        output= cur.fetchall()
        target =output[0]["volume_path"]
        Container_name=output[0]["containername"]
        projectname=output[0]["project_name"]
        print(projectname)
        

        source=config[projectname]['path']
        allfiles = os.listdir(source)

        for i in allfiles:
            print(i)    
            src_path_dir = os.path.join(source, i)
            dst_path_dir = os.path.join(target,i)
    
            if(os.path.isfile(src_path_dir)==True):
                shutil.copyfile(src_path_dir,dst_path_dir)
                os.remove(src_path_dir)
                print("copied sucessfully")
            else:     
                    if(os.path.exists(dst_path_dir)):
                        shutil.rmtree(dst_path_dir) 
                        shutil.move(src_path_dir,target) 
                        print("copied sucessfully")
                    else:   
                        shutil.move(src_path_dir,target) 
                        print("copied sucessfully")
           
        command=f"docker restart {Container_name}"
        cmd2 = os.system(command)  
        print(cmd2)   
            # command=f"docker restart {Container_name}"
            # cmd2 = os.system(command)  
            # print(cmd2)
                  
        goodmessage="migrated sucessfully"    
    except Exception as e :
                    flag=False
                    print(e)
                    return jsonify('Failed')  
    finally:
        cur.close()
        if flag:
             positiveData = {'message': 'migrated successfully'}
             return make_response(jsonify(positiveData), 200)

        else:
             
             negativeData = {'message': 'migration Failed'}
             return make_response(jsonify(negativeData), 200)                        
    


def Restart(Container_name):
    command=f"docker restart {Container_name}"
    cmd2 = os.system(command)  
    print(cmd2)
    
    
@app.route('/migrateall',methods=['POST'])
def CopyAllToTarget():
    flag=True
    conn = pymysql.connect(
        host = '159.89.168.228',
        user = 'root',
        password = 'prod',
        db='DevopsAdmin'
        
    )
    fileid = request.json['fileid']
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        
        for projectid in fileid:
            
            result= cur.execute("SELECT p.volume_path,p.containername,p.project_name FROM project_details p, filedetails f WHERE f.id=%s AND p.project_id=f.project_id",(projectid,))

            output = cur.fetchall()
            target =output[0]["volume_path"]
            Container_name=output[0]["containername"]
            projectname=output[0]["project_name"]
            print(projectname)
            source=config[projectname]['path']
            allfiles = os.listdir(source)
            try:
                for i in allfiles:
                  print(i)    
                  src_path_dir = os.path.join(source, i)
                  dst_path_dir = os.path.join(target,i)
    
                  if(os.path.isfile(src_path_dir)==True):
                    shutil.copyfile(src_path_dir,dst_path_dir)
                    os.remove(src_path_dir)
                    print("copied sucessfully")
                  else:     
                      if(os.path.exists(dst_path_dir)):
                        shutil.rmtree(dst_path_dir) 
                        shutil.move(src_path_dir,target) 
                        print("copied sucessfully")
                      else:   
                        shutil.move(src_path_dir,target) 
                        print("copied sucessfully")
           
                
              
            except:
                flag=False
            # command=f"docker restart {Container_name}"
            # cmd2 = os.system(command) 
            # print(cmd2)
        proc = multiprocessing.Process(target=Restart(Container_name), args=())
        proc.start()          
          
    except Exception as e:
                    flag=False
                    return jsonify('Failed')  
    finally:
        cur.close()
        if flag:
             positiveData = {'message': 'migrated successfully'}
             return make_response(jsonify(positiveData), 200)

        else:
             
             negativeData = {'message': 'Failed'}
             return make_response(jsonify(negativeData), 200)                        
    

if __name__ == '__main__':

        app.run(debug=True,host='0.0.0.0',port=12000)