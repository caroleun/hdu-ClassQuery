# -*- coding: utf-8 -*-
import requests
import re
from Login import des_py


def getPage(url) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    html = response.text
    return html


def save(content, filepath: str):
    with open(filepath, 'w') as fp:
        fp.write(str(content))


class Login:
    # 教师端
    url_teacher = 'http://cas.hdu.edu.cn/cas/login?service=http://jxglteacher.hdu.edu.cn/index.aspx'
    url_student = 'http://cas.hdu.edu.cn/cas/login?service=http://jxgl.hdu.edu.cn/default.aspx'

    def __init__(self, username: str, password: str, teacher: bool = False):
        if teacher:
            self.url = Login.url_teacher
        else:
            self.url = Login.url_student
        self.html = getPage(self.url)
        self.un = username
        self.ul = len(self.un)
        self.pd = password
        self.pl = len(self.pd)
        self.lt = self.parse_lt()
        # self.rsa = des_py.callJs('strEnc',
        #                          self.un + self.pd + self.lt,
        #                          '1', '2', '3'
        #                          )
        self.rsa = des_py.strEnc(self.un + self.pd + self.lt, '1', '2', '3')
        self.execution = self.parse_execution()
        self._eventId = self.parse_eventId()
        self.dataForm = f'rsa={self.rsa}&ul={self.ul}&pl={self.pl}&lt={self.lt}' \
            f'&execution={self.execution}&_eventId={self._eventId}'

        self.session = requests.Session()
        self.session.get(self.url)  # 先get请求将JSESSIONID保存在session里
        self.url_ticket = self.login_post()
        # print(self.url_ticket)
        self.cookie = self.login_get()

    def parse_lt(self) -> str:
        # html_tree = etree.HTML(self.html)
        # return html_tree.xpath('//input[@id="lt"]/@value')[0]
        match = re.search('<input type="hidden" id="lt" name="lt" value="(.+?)" />', self.html)
        return match.group(1)

    def parse_execution(self) -> str:
        # html_tree = etree.HTML(self.html)
        # return html_tree.xpath('//form[@id="loginForm"]//input[@name="execution"]/@value')[0]
        return re.search('<input type="hidden" name="execution" value="(.+?)" />', self.html).group(1)

    def parse_eventId(self) -> str:
        # html_tree = etree.HTML(self.html)
        # return html_tree.xpath('//form[@id="loginForm"]//input[@name="_eventId"]/@value')
        return re.search('<input type="hidden" name="_eventId" value="(.+?)" />', self.html).group(1)

    def login_post(self) -> str:
        post_headers = {
            # 'Host': 'cas.hdu.edu.cn',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            # 'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            # 'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Content-Length': '333',
            # 'Connection': 'keep-alive',
            # 'Referer': 'http://cas.hdu.edu.cn/cas/login?service=http://jxgl.hdu.edu.cn/default.aspx',

            # 'Upgrade-Insecure-Requests': '1'
        }
        response = self.session.post(self.url, data=self.dataForm, headers=post_headers, allow_redirects=False)
        assert response.status_code == 302  # 未重定向
        url_location = response.headers.get('Location')
        if not url_location:
            raise Exception('未获取到ticket url.')
        return url_location

    def login_get(self) -> str:
        """return cookie"""
        response = requests.head(self.url_ticket)
        cookie = str(response.headers.get('Set-Cookie'))
        return cookie


def test():
    username = input()
    password = input()
    login = Login(username, password)
    cookie = login.cookie
    print(cookie)


if __name__ == '__main__':
    test()
