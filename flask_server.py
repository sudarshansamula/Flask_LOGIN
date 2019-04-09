from flask import Flask,render_template,request,session
import mysql.connector
from mysql.connector import Error
import json
import os
db_config={
    "host":'localhost',
    "database":'NetElixir',
    "user":"root",
    "password":"root123456"
}
cwd = os.getcwd()
app=Flask(__name__)
app.secret_key='supersecretkey'
@app.route("/")
def loadAllFiles():
    return  render_template('home.html')
@app.route("/login",methods=["GET","POST"])
def loginUser():
    data={'email':"",'password':""}
    if request.method == "POST":
        data['email']=request.form["email"]
        data['password']=request.form["password"]
    if valiDateExistingorNOt(data):
        return render_template('admin.html')
    else:
        return render_template('home.html')
@app.route("/getUsersInfo",methods=["GET","POST"])
def getUsersInfo():
    sql_query = "select *from user_info where user_type ='user'"
    connObj = getDBconnection()
    if session.get('isAdmin'):
      sql_query = "select *from user_info"
    res_obj = {}
    connObj["cursor"].execute(sql_query)
    sel_rows = connObj["cursor"].fetchall()
    closeConnections(connObj)
    res_obj = {"message":"success","data":sel_rows,"isAdmin":session.get('isAdmin')}    
    return json.dumps(res_obj)
def  valiDateExistingorNOt(data):
    email = data['email']
    #password = data['password']
    sel_qry="select * from user_info where email="+json.dumps(email)
    try:
        connObj=getDBconnection()
        connObj["cursor"].execute(sel_qry)
        sel_rows = connObj["cursor"].fetchall()
        closeConnections(connObj)
        isAdmin=False
        if sel_rows[0]['user_type'] == "admin":
            isAdmin=True
        session['isAdmin']=isAdmin
        return  True
    except Error as e:
        print('Error throwing while connecting to the database',e)
        return  False
def getDBconnection():
    mySQLconnection=mysql.connector.connect(host=db_config["host"],database=db_config["database"],user=db_config['user'],password=db_config['password'])
    return {"cursor":mySQLconnection.cursor(dictionary=True),"conn":mySQLconnection}
def closeConnections(connObj):
    connObj["cursor"].close()
    connObj["conn"].close()
@app.route("/logout")
def logout():
    session.clear()
    return render_template('home.html')
@app.route("/createUser",methods=["GET","POST"])
def createUser():
    connObj =getDBconnection()
    insertObj=json.loads(request.args.get('insertInfo'))
    print("insert_obj****",insertObj)
    email=insertObj['email']
    name=insertObj['name']
    password=insertObj['password']
    user_type=insertObj['user_type']
    feed_back=insertObj['feed_back']
    insert_query ="""insert into user_info(email,password,name,user_type,feed_back) values(%s,%s,%s,%s,%s)"""
    res_obj = {}
    valuesArr=(email,password,name,user_type,feed_back)
    try:
        connObj["cursor"].execute(insert_query,valuesArr)
        connObj["conn"].commit()
        closeConnections(connObj)
        res_obj = {"message":"success","data":"Create User Successfully"}
        return json.dumps(res_obj)
    except Error as e:
        print("Exp***",e)
        res_obj = {"message":"failure","data":"Sorry, unable process your request"}
        closeConnections(connObj)
        return json.dumps(res_obj)
@app.route("/deleteUser")
def deleteUser():
    connObj=getDBconnection()
    dltID=request.args.get('id')
    dltquery="delete from user_info where id="+dltID
    try:
        connObj["cursor"].execute(dltquery)
        connObj["conn"].commit()
        res_obj = {"message":"success","data":"Deleted User Successfully"}
    except Error as e:
        print("Exception***",e)
        res_obj = {"message":"failure","data":"Sorry, unable process your request"}
    return json.dumps(res_obj)
if __name__=="__main__":
    app.run(debug=True,port=5003)
