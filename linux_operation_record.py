#!/usr/bin/python3
# -*- coding:utf-8 -*-
# create by binwu!
# time: 2017/12/10 22:44:28

from tornado import web,httpserver,ioloop,escape
from psutil import disk_usage
import database
import os
import json


#定义内容页面每页显示条目数
item_num = 20

#定义管理员用户代码
ADMIN_TYPE = 1
#定义普通用户类型
ORD_TYPE = 2


def init():
    global item_num
    item_num = int(database.query_mysql_setting(oprset = 'item_num')[0][0])
    return


class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie(name = 'username')

    def get_current_usertype(self):
        global curr_username
        curr_username = self.current_user.decode('utf-8')
        db_result = database.get_password_from_mysql(curr_username)
        if db_result:
            global curr_username_type
            curr_username_type = db_result[0][1]
            return curr_username_type
        else:
            return None



class IndexHandler(BaseHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')


class LoginHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        self.render('index.html')

    def post(self, *args, **kwargs):
        name = self.get_argument('username')
        pw = self.get_argument('password')
        # print(name,pw)
        password = database.get_password_from_mysql(name)
        if len(password) == 1:
            if database.get_hash(pw) == password[0][0]:
                self.set_secure_cookie(name = 'username', value = name, expires_days = None )
                self.set_secure_cookie(name = 'userid', value = str(password[0][3]), expires_days = None )
                self.set_secure_cookie(name = 'authid', value = password[0][2], expires_days = None )
                self.redirect('/welcome')
            else:
                self.redirect('/')
        else:
            self.redirect('/')


class WelcomeHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        host_headers = self.request.headers
        self.render('welcome.html', user=self.current_user,usertype = self.get_current_usertype(),admin_type = ADMIN_TYPE,host_ip=host_headers['x-forwarded-for'])

class LogoutHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if self.get_argument("logout", None):
            self.clear_cookie('username')
            self.clear_cookie('userid')
            self.clear_cookie('authid')
            self.redirect('/')
            print('退出登录完毕')


class NewrecordeHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        self.render('newrecorde.html')


class CompleteHandler(BaseHandler):
    @web.authenticated
    def post(self, *args, **kwargs):
        user = self.get_argument('user')
        content = self.get_argument('content')
        if user and content :
            loginuser = escape.xhtml_escape(self.current_user)
            result = database.inset_to_mysql(user,content,loginuser,create_id=int(self.get_secure_cookie(name="userid")))
            if not len(result):
                self.render('complete.html')
            else:
                self.render('error.html')
        else:
            self.render('error.html')

class ContentHandler(BaseHandler):
    @web.authenticated
    def get(self, page):    #将url中的页面参数传递给page变量
        current_page = int(page)
        #print("current_page:%d" % current_page)
        if current_page > 0:
            if curr_username_type == ADMIN_TYPE:        #admin用户则查询所有记录
                total_count = database.query_mysql_table_count(table_name='T_CONTENT')
            else:
                authid_str = str(self.get_secure_cookie(name = 'authid').decode('utf-8'))
                authid_list = authid_str.split(".")
                authid_length = len(authid_list)
                sql = "SELECT count(*) FROM T_CONTENT WHERE"
                for index, i in enumerate(authid_list):
                    if index == authid_length - 1:  # 判断是否为最后一个元素
                        sql = sql + " " + "createid=" + i + ";"
                    else:
                        sql = sql + " " + "createid=" + i + " " + "OR"
                total_count = database.exe_mysql_sql(sql=sql)
            #print("total_count:%d" %total_count[0][0])
            #print(total_count)
            global item_num
            if total_count[0][0] > item_num:
                    total_page = total_count[0][0] // item_num + 1
            else:
                    total_page = 1
            #print("total_page:%d" % total_page)
            start_item = (current_page - 1)*item_num
            if current_page > 1 and current_page <= total_page:
                back_page = current_page - 1
            elif current_page == 1:
                  back_page = 1
            else:
                self.render('error.html')
            #print("back_page:%d" % back_page)
            if current_page < total_page and current_page >= 1:
                next_page = current_page + 1
            elif current_page == total_page:
                next_page = current_page
            else:
                self.render('error.html')

            if curr_username_type == ADMIN_TYPE:  # admin用户则查询所有记录
                content = database.read_from_mysql_limit(org=start_item,rows=item_num)
            else:
                sql_content = "SELECT * FROM T_CONTENT WHERE"
                for index, i in enumerate(authid_list):
                    if index == authid_length - 1:  # 判断是否为最后一个元素
                        sql_content = sql_content + " " + "createid=" + i + " " + "ORDER BY id DESC LIMIT %d,%d" % (start_item,item_num) + ";"
                    else:
                        sql_content = sql_content + " " + "createid=" + i + " " + "OR"
                content = database.exe_mysql_sql(sql=sql_content)
            #content = database.read_from_mysql(20)
            #print(content)
            if len(content):
                self.render('content.html',contentlist=content,backpage=back_page,nextpage=next_page,endpage=total_page,cupage=current_page,allpage=total_page)
            else:
                self.render('error.html')
        else:
            self.render('error.html')


class SearchHandler(BaseHandler):
    @web.authenticated
    def get(self, page):    #将url中的页面参数传递给page变量
        current_page = int(page)
        # print("current_page:%d" % current_page)
        global search_result
        total_count = len(search_result)
        if current_page > 0:
            global item_num
            if total_count > item_num:
                total_page = total_count // item_num
            else:
                total_page = 1
            # print("total_page:%d" % total_page)
            start_item = (current_page - 1) * item_num
            if current_page > 1 and current_page <= total_page:
                back_page = current_page - 1
            elif current_page == 1:
                back_page = 1
            else:
                self.render('error.html')
            # print("back_page:%d" % back_page)
            if current_page < total_page and current_page >= 1:
                next_page = current_page + 1
            elif current_page == total_page:
                next_page = current_page
            else:
                self.render('error.html')
            content = search_result[start_item:start_item + item_num]
            # content = database.read_from_mysql(20)
            if len(content):
                # print(content)
                self.render('searchresult.html', contentlist=content, backpage=back_page, nextpage=next_page,
                            endpage=total_page, cupage=current_page, allpage=total_page)
            else:
                self.render('contentnull.html')
        else:
            self.render('error.html')


    @web.authenticated
    def post(self, *args, **kwargs):
        key = self.get_argument('key')
        global search_result
        if curr_username_type == ADMIN_TYPE:  # admin用户则查询所有记录
            search_result = database.search_mysql(table_name='T_CONTENT',field='content',key=key)
        else:
            authid_str = str(self.get_secure_cookie(name='authid').decode('utf-8'))
            authid_list = authid_str.split(".")
            authid_length = len(authid_list)
            sql_content = "SELECT * FROM T_CONTENT WHERE content LIKE '%{}%' AND".format(key)
            for index, i in enumerate(authid_list):
                if index == authid_length - 1:  # 判断是否为最后一个元素
                    sql_content = sql_content + " " + "createid=" + i + " " + "ORDER BY id DESC" + ";"
                else:
                    sql_content = sql_content + " " + "createid=" + i + " " + "OR"
            print(sql_content)
            search_result = database.exe_mysql_sql(sql=sql_content)
        # print(search_result)
        # print(len(search_result))
        current_page = 1
        total_count = len(search_result)
        global item_num
        if total_count > item_num:
            total_page = total_count // item_num
        else:
            total_page = 1
        # print("total_page:%d" % total_page)
        # start_item = (current_page - 1) * item_num
        back_page = 1
        if current_page < total_page and current_page >= 1:
            next_page = current_page + 1
        elif current_page == total_page:
            next_page = current_page
        else:
            self.render('error.html')

        content = search_result[0:item_num]
        # content = database.read_from_mysql(20)
        if len(content):
            # print(content)
            self.render('searchresult.html', contentlist=content, backpage=back_page, nextpage=next_page, endpage=total_page,
                        cupage=current_page, allpage=total_page)
        else:
            self.render('contentnull.html')




class NewpasswordHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        self.render('newpassword.html')

class PwsuccessHandler(BaseHandler):
    @web.authenticated
    def post(self, *args, **kwargs):
        oldpassword = self.get_argument('oldpassword')
        newpassword1 = self.get_argument('newpassword1')
        newpassword2 = self.get_argument('newpassword2')
        name = escape.xhtml_escape(self.current_user)
        hasholdpassword = database.get_hash(oldpassword)
        password = database.get_password_from_mysql(name)
        if hasholdpassword == password[0][0] and newpassword1 == newpassword2:
            if not len(database.modify_password_mysql(username=name,newpassword=database.get_hash(newpassword1))):
                self.clear_cookie('username')
                self.render('pwsuccess.html')
            else:
                self.render('error.html')
        else:
            self.render('error.html')


class MoreHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            host_headers = self.request.headers
            self.render('more.html',user = curr_username,usertype = curr_username_type,admin_type = ADMIN_TYPE,host_ip=host_headers['x-forwarded-for'])
        else:
            self.redirect('/welcome')


class RegisterHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            self.render('register.html',user = curr_username)
        else:
            self.redirect('/welcome')

    @web.authenticated
    def post(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            new_username = self.get_argument('username')
            new_password = self.get_argument('password')
            new_password2 = self.get_argument('password2')
            realname = self.get_argument('realname')
            new_usertype = self.get_argument('user_type')
            new_usertype = int(new_usertype)
            if new_password == new_password2 and (new_usertype == ADMIN_TYPE or new_usertype == ORD_TYPE):
                if not len(database.query_mysql_username(new_username)):
                    hashnew_password = database.get_hash(new_password)
                    if not len(database.add_user_T_USER(name=new_username,password=hashnew_password,usertype=new_usertype,realname=realname)):
                        new_user_id = database.query_user_self_id(name=new_username)
                        if len(new_user_id):
                            database.updata_user_self_auth(id = new_user_id[0][0])
                            self.render('addusersuccess.html',user = new_username)
                        else:
                            self.write('错误！更新用户权限错误，请返回！')
                    else:
                        self.write('错误！添加用户出错，请返回重新输入！')
                else:
                    self.write('错误！用户名已注册，请返回重新输入用户名！')
            else:
                self.render('error.html')
        else:
            self.redirect('/welcome')



class DeluserHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            self.render('deluser.html')
        else:
            self.redirect('/welcome')

    @web.authenticated
    def post(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            del_username = self.get_argument('delusername')
            if len(database.query_mysql_username(name = del_username)):
                del_result = database.delete_mysql_user(name=del_username)
                if not len(del_result):
                    self.render('delusersuccess.html', user=del_username)
                else:
                    self.render('error.html')
            else:
                self.render('no_user.html',user = del_username)
        else:
            self.redirect('/welcome')



class ResetpasswordHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            self.render('resetpassword.html')
        else:
            self.redirect('/welcome')

    @web.authenticated
    def post(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            reset_username = self.get_argument('resetusername')
            new_password1 = self.get_argument('newpassword1')
            new_password2 = self.get_argument('newpassword2')
            if new_password1 == new_password2:
                if len(database.query_mysql_username(name=reset_username)):
                    if not len(database.modify_password_mysql(username=reset_username, newpassword=database.get_hash(new_password1))):
                        self.render('resetpwsuccess.html',user = reset_username)
                else:
                    self.render('retpw_no_user.html', user=reset_username)
            else:
                self.write('错误！两次输入的密码不一致！请返回重新输入。')
        else:
            self.redirect('/welcome')




class ModifycontentHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            self.render('selectid.html')
        else:
            self.redirect('/welcome')

    @web.authenticated
    def post(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            global content_id
            try:
                content_id = int(self.get_argument('id'))
            except:
                self.write('错误！您输入的文章序号必须为正整数，请返回重新输入！')
                return
            result_content = database.query_mysql_content(id = content_id)
            if len(result_content):
                self.render('editcontent.html',oprname = result_content[0][1],oprcontent = result_content[0][0])
            else:
                self.write('错误！您输入的记录序号不正确，请返回重新输入！')
        else:
            self.redirect('/welcome')


class EditcontentHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            self.render('editcomplete.html')
        else:
            self.redirect('/welcome')

    @web.authenticated
    def post(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            new_user = self.get_argument('newuser')
            new_content = self.get_argument('newcontent')
            if new_user and new_content:
                update_result = database.modify_mysql_content(id = content_id,opruser = new_user,oprcontent = new_content)
                if not len(update_result):
                    self.render('editcomplete.html')
                else:
                    self.render('error.html')
            else:
                self.render('error.html')
        else:
            self.redirect('/welcome')



class DelcontentHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            self.render('delcontentid.html')
        else:
            self.redirect('/welcome')

    @web.authenticated
    def post(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            try:
                del_id = int(self.get_argument('id'))
            except:
                self.write('错误！您输入的记录序号必须为正整数，请返回重新输入！')
                return
            del_result = database.delete_mysql_content(id = del_id)
            if not len(del_result):
                self.render('delcontentsuccess.html',id = del_id)
            else:
                self.render('error.html')
        else:
            self.redirect('/welcome')



class ChangeitemHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            self.render('changeitem.html',item = item_num)
        else:
            self.redirect('/welcome')

    @web.authenticated
    def post(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            try:
                new_item = int(self.get_argument('newitem'))
            except:
                self.write('错误！您输入的记录序号必须为正整数，请返回重新输入！')
                return
            if new_item >= 1:
                global item_num
                item_num = new_item
                database.modify_mysql_setting(oprset = 'item_num',oprvalue = new_item)
                self.render('changeitemsuccess.html',item = item_num)
            else:
                self.write('错误！请返回输入大于1的正整数！')
        else:
            self.redirect('/welcome')


class SetauthHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            users_db = database.query_mysql_user_all()
            self.render('setauth.html', user = curr_username,users = users_db)
        else:
            self.redirect('/welcome')

    @web.authenticated
    def post(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            web_souruser = self.get_arguments('souruser')
            web_authid = self.get_arguments('authid')
            str_authid = '.'.join(web_authid) #将列表转换为字符串存数据库
            for intodb_sourid in web_souruser:
                if len(database.modify_T_USER_auth(int(intodb_sourid), str_authid)):
                    self.render('error.html')
                    break
            self.render('setauthsuccess.html',authuser = web_souruser)
        else:
            self.redirect('/welcome')


class QueryauthHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            users_db = database.query_mysql_user_all()
            self.render('queryauth.html', user = curr_username,users = users_db)
        else:
            self.redirect('/welcome')

    @web.authenticated
    def post(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            web_queryuser = self.get_argument('queryuser')
            authid_db_tuple = database.query_mysql_user_authid_by_id(id = int(web_queryuser))
            if authid_db_tuple:
                authid_db_str = authid_db_tuple[0][0]
                authidlist = authid_db_str.split(".")
                auth_length = len(authidlist)
                sql = "SELECT id,username,realname FROM T_USER WHERE"
                for index,i in enumerate(authidlist):
                    if index == auth_length - 1:    #判断是否为最后一个元素
                        sql = sql + " "+"id="+i+";"
                    else:
                        sql = sql + " " + "id=" + i + " " + "OR"
                autheduser = database.exe_mysql_sql(sql = sql)
                self.render('queryauthresult.html', user=curr_username, users=autheduser)
            else:
                self.render('error.html')
        else:
            self.redirect('/welcome')



class ShowHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            host_headers = self.request.headers
            self.render('show.html', user=curr_username,host_ip=host_headers['x-forwarded-for'])
        else:
            self.redirect('/welcome')



class DiskHandler(BaseHandler):
    @web.authenticated
    def get(self, *args, **kwargs):
        if curr_username_type == ADMIN_TYPE:
            legendData = ["'/'已使用(MB)", "'/'未使用(MB)"]
            seriesData = []
            selected = {"'/'已使用(MB)": 1, "'/'未使用(MB)": 1}  # 字典中有，且值为0为未选中
            disk_status = disk_usage('/')
            for i in range(2):
                seriesData.insert(i, {"name": legendData[i], "value": disk_status[i+1]/1024/1024})
            data_dic = {"legendData": legendData, "seriesData": seriesData, "selected": selected}
            data_json = json.dumps(data_dic, ensure_ascii=False)
            self.finish(data_json)




setting = {
    'template_path':'templates',
    'static_path':'static',
    'static_url_prefix':'/static/',
    "cookie_secret": os.urandom(44),
    "xsrf_cookies": True,
    "login_url": "/",
}

application = web.Application([
            (r"/",IndexHandler),
            (r"/login",LoginHandler),
            (r"/welcome",WelcomeHandler),
            (r"/logout",LogoutHandler),
            (r"/newrecorde",NewrecordeHandler),
            (r"/complete",CompleteHandler),
            (r"/content/(\d*?)",ContentHandler),
            (r"/newpassword",NewpasswordHandler),
            (r"/pwsuccess",PwsuccessHandler),
            (r"/more",MoreHandler),
            (r"/register",RegisterHandler),
            (r"/deluser",DeluserHandler),
            (r"/resetpassword",ResetpasswordHandler),
            (r"/modifycontent",ModifycontentHandler),
            (r"/editcontent",EditcontentHandler),
            (r"/delcontent",DelcontentHandler),
            (r"/changeitem",ChangeitemHandler),
            (r"/search/(\d*?)",SearchHandler),
            (r"/setauth",SetauthHandler),
            (r"/queryauth",QueryauthHandler),
            (r"/show",ShowHandler),
            (r"/show/disk",DiskHandler),
            ],**setting)

if __name__ == '__main__':
    init()
    http_server = httpserver.HTTPServer(application,xheaders=True)
    http_server.listen(8381)
    print("http://127.0.0.1:8381/  is runing!")
    ioloop.IOLoop.current().start()
