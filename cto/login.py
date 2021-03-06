# -*- coding: utf-8 -*-
import pickle,requests,os
from cto.urls import urls
from lxml import etree
from cto import tools

# 自动登录类
class Login(object):
    headers = {
        "Accept": "text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8",
        "Accept - Encoding": "gzip, deflate",
        "Accept - Language": "zh - CN, zh;q = 0.9, en;q = 0.8",
        "Connection": "keep - alive",
        "DNT": "1",
        "Upgrade - Insecure - Requests": "1",
        'Host': 'home.51cto.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
    }

    # 初始化缓存信息路径
    def __init__(self):
        self.cache_path = tools.join_path(tools.main_path(), 'cache')
        tools.check_or_make_dir(self.cache_path)
        self.path = {
            'auth': tools.join_path(self.cache_path, "auth"),
            'cookies': tools.join_path(self.cache_path, "cookies"),
        }
        pass

    def login(self):
        session = requests.Session()
        result = self.check_cookies(session)
        if result:
            return result
        else:
            result = self.check_auth(session)
            if result:
                return result
            else:
                result = False
                while not result:
                    print('账号或密码错误')
                    result = self.re_login(session)
                print('重新登陆成功')
                return result

    def re_login(self, session):
        print("请重新登录")
        username = raw_input('登录账号:')
        password = raw_input('密码:')
        auth = {
            'username': username.strip(),
            'password': password.strip()
        }

        return self.login_with_auth(session,auth)


    def is_login_avalid(self,session):
        resp = session.get(urls['sign'])
        text = resp.text
        if len(text) < 100:
            print('cookies登陆成功')
            return session
        else:
            return False
    def check_auth(self,session):
        if os.path.exists(self.path['auth']):
            # 从文件中读取cookie
            with open(self.path['auth'], 'r') as f:
                auth = pickle.load(f)

            headers = self.headers
            headers['host'] = 'edu.51cto.com'
            headers['referer'] = 'edu.51cto.com/center/course/user/get-study-course'
            session.headers = headers

            if self.login_with_auth(session,auth):
                print('auth登陆成功')
                return session
            else:
                print("账号或密码失效")
                print("请重新登录")
                return False
        else:
            return False

    def check_cookies(self,session):
        if os.path.exists(self.path['cookies']):
            # 从文件中读取cookie
            with open(self.path['cookies'], 'r') as f:
                #qxx 移除_identity的cookie, 实测这个cookie会导致课程列表没数据; 
                d = dict(pickle.load(f))
                d.pop("_identity",None)
                cookies = requests.utils.cookiejar_from_dict(d)
            session.cookies = cookies
            headers = self.headers
            headers['Host'] = 'edu.51cto.com'
            headers['Referer'] = 'edu.51cto.com/center/course/user/get-study-course'
            session.headers = headers

            if self.is_login_avalid(session):
                return session
            else:
                print("cookies失效")
                return False
        else:
            return False

    def login_with_auth(self,session,auth):
        headers = self.headers

        resp = session.get(urls['login'], headers=headers)
        html = etree.HTML(resp.text)
        csrf = html.xpath('//input[@name="_csrf"]/@value')[0]

        data = {
            "_csrf": csrf,
            "LoginForm[username]": auth['username'],
            "LoginForm[password]": auth['password'],
            "LoginForm[rememberMe]": 1,
            "login - button": "登录"
        }

        resp = session.post(urls['login'], data=data)

        if 'Set-Cookie' in resp.headers:

            with open(self.path['auth'], 'w') as f:
                pickle.dump(auth, f)
            with open(self.path['cookies'], 'w') as f:
                pickle.dump(requests.utils.dict_from_cookiejar(session.cookies), f)
            return session
        else:
            return False

if __name__ == '__main__':
    login = Login()
    login.login()

