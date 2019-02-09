# _*_ coding:utf-8 _*_
# created by binwu!
# time: 2017/12/13 09:47:29
# version: 2.0

import database as db
import time

if __name__ == '__main__':
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    username = 'binwu'
    mima = '1234'
    password = db.get_hash(mima)
    mysql = ("INSERT INTO T_USER(username,password,usertype,c_time) VALUES ('%s','%s',2,'%s');") % (username,password,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    # mysql = ("INSERT INTO T_SETTING(oprset,oprvalue,c_time) VALUES ('item_num',20,'%s');") % time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    print(mysql)
    # mysql2 = 'select * from T_USER;'
    mysqlcon = db.connectmysql()
    mysqlcur = db.getmysqlcur(mysqlcon)
    result = db.exemysql(mysqlcur, mysql)
    db.closemysqlcur(mysqlcur)
    db.closemysql(mysqlcon)
    print(result)
