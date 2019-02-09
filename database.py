# _*_ coding:utf-8 _*_



import pymysql
import time
import hashlib

def connectmysql():
    config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'passwd': 'qqsg2000C',
            'db': 'opr',
            'charset': 'utf8'
        }  # 链接的配置字典信息
    try:
        mysql = pymysql.connect(**config)
        return mysql
       #mysql.commit()
        cur.close()
    except pymysql.Error as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))


def getmysqlcur(connection):
    try:
        return connection.cursor()
    except pymysql.Error as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))

def exemysql(cur,sql):
    try:
        cur.execute(sql)
        return cur.fetchall()
    except pymysql.Error as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))


def closemysqlcur(cur):
    try:
        cur.close()
    except pymysql.Error as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))


def closemysql(connection):
    try:
        connection.commit()
        connection.close()
    except pymysql.Error as e:
        print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        connection.rollback()    #发生错误时回滚


def get_password_from_mysql(username):
    mysql = "SELECT password,usertype,authid,id FROM T_USER WHERE username = '%s';" % username
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    password = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return password

def inset_to_mysql(user,content,loginuser,create_id):
    mysql = "INSERT INTO T_CONTENT(content,opruser,loginuser,oprtype,c_time,createid) VALUES ('%s','%s','%s',1,'%s',%d);" % (content,user,loginuser,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),create_id)
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def read_from_mysql(rows=10):
    mysql = "SELECT * FROM T_CONTENT ORDER BY id DESC LIMIT %d;" % rows
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def modify_password_mysql(username,newpassword):
    mysql = "UPDATE T_USER SET password='%s' WHERE username='%s';" % (newpassword,username)
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def query_mysql_table_count(table_name='T_CONTENT'):
    mysql = "SELECT count(*) FROM %s;" % table_name
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def read_from_mysql_limit(org=0,rows=20):
    mysql = "SELECT * FROM T_CONTENT ORDER BY id DESC LIMIT %d,%d;" % (org,rows)
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def get_hash(word):
    md5 = hashlib.md5(word.encode('utf-8')).hexdigest()
    return md5

def query_mysql_username(name):
    mysql = "SELECT username FROM T_USER WHERE username='%s';" % name
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def query_mysql_user_noadmin():
    mysql = "SELECT id,username,realname FROM T_USER WHERE usertype!=1;"
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def query_mysql_user_all():
    mysql = "SELECT id,username,realname FROM T_USER;"
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def query_mysql_user_authid_by_id(id):
    mysql = "SELECT authid FROM T_USER WHERE id=%d;" % id
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def query_mysql_user_by_id(id):
    mysql = "SELECT username,realname FROM T_USER WHERE id=%d;" % id
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def add_user_T_USER(name,password,usertype,realname):
    mysql = "INSERT INTO T_USER(username,password,usertype,c_time,realname) VALUES ('%s','%s',%d,'%s','%s');" % (name,password,usertype,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),realname)
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def query_user_self_id(name):
    mysql = "SELECT id FROM T_USER WHERE username='%s';" % name
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def updata_user_self_auth(id):
    mysql1 = "UPDATE T_USER SET authid='%s' WHERE id=%d;" % (str(id),id)
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result1 = exemysql(mysqlcur, mysql1)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result1


def modify_T_USER_auth(sourid,authid):
    mysql = "UPDATE T_USER SET authid='%s' WHERE id=%d;" % (authid,sourid)
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def delete_mysql_user(name):
    mysql = "DELETE FROM T_USER WHERE username='%s';" % name
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result


def query_mysql_content(id):
    mysql = "SELECT content,opruser,oprtype FROM T_CONTENT WHERE id=%d;" % id
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result


def modify_mysql_content(id,opruser,oprcontent):
    mysql = "UPDATE T_CONTENT SET opruser='%s',content='%s' WHERE id=%d;" % (opruser,oprcontent,id)
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result


def delete_mysql_content(id):
    mysql = "DELETE FROM T_CONTENT WHERE id=%d;" % id
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result


def query_mysql_setting(oprset):
    mysql = "SELECT oprvalue FROM T_SETTING WHERE oprset='%s';" % oprset
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result


def modify_mysql_setting(oprset,oprvalue):
    mysql = "UPDATE T_SETTING SET oprvalue=%d,c_time='%s' WHERE oprset='%s';" % (oprvalue,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),oprset)
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result


def search_mysql(table_name='T_CONTENT',field='content',key='NOLL'):
    mysql = "SELECT * FROM {} WHERE {} LIKE '%{}%' ORDER BY id DESC;".format(table_name,field,key)
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result

def exe_mysql_sql(sql):
    mysql = "%s" % sql
    mysqlcon = connectmysql()
    mysqlcur = getmysqlcur(mysqlcon)
    result = exemysql(mysqlcur, mysql)
    closemysqlcur(mysqlcur)
    closemysql(mysqlcon)
    return result