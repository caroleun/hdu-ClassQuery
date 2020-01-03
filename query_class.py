# -*- coding: utf-8 -*-
import json
import re
import requests
from urllib.request import unquote, quote
from lxml import etree
from bs4 import BeautifulSoup
from Login.login import Login
from class_models import Modules


class QueryClass:
    def __init__(self, username: str, password: str, module_name: str = '', ywyl: str = '有', teacher: bool = False):
        self.username = username
        self.password = password
        self.cookie = Login(username, password, teacher).cookie
        self.ywyl = ywyl

        self.modules = Modules(username, self.cookie)
        if not module_name:
            module_name = '通识选修课'
        self.module_url = self.modules.get_module_url(module_name)
        self.html_module_index = QueryClass.get_html(self.module_url, headers={'Referer': self.modules.url_index,
                                                                               'Cookie': self.cookie})

    def get_module_url(self, module_name: str):
        """返回指定模块的url"""
        return self.modules.get_module_url(module_name)

    def get_class_info(self):
        params = self.get_params()
        headers = {'Host': 'jxgl.hdu.edu.cn',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
                   'Referer': QueryClass.get_reference_url(self.module_url),
                   'Cookie': self.cookie
        }
        response = requests.post(self.module_url, headers=headers, data=params)
        html = response.text
        print(html)
        class_list = QueryClass.parse_class_html(html)

    @staticmethod
    def parse_class_html(html) -> list:
        trs = BeautifulSoup(html, 'lxml').find('table', {'class': "datelist"}).findAll('tr')
        length = len(trs)
        if length <= 1:
            return []
        print(length)
        class_list = []
        td_0 = trs[0].findAll('td')
        number_of_td = len(td_0)
        for i in range(1, length):
            tds = trs[i].findAll('td')
            dct = {}
            for j in range(2, number_of_td):
                dct[td_0[j].text] = tds[j].text.strip()
            class_list.append(dct)
        QueryClass.save_json(class_list, 'class.json')
        return class_list

    @staticmethod
    def save_json(class_list: list, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as fp:
            json.dump(class_list, fp)

    @staticmethod
    def get_reference_url(module_url: str):
        match_obj = re.search('xm=(.+)', module_url)
        string_source = match_obj.group(1)
        url_quote = module_url.replace(string_source, quote(string_source))
        return url_quote

    def get_params(self) -> str:
        """从第一次选课模块get请求返回html中获取post请求的data表单参数"""
        view_state_xpath = '//*[@id="__VIEWSTATE"]/@value'
        view_validation_xpath = '//*[@id="__EVENTVALIDATION"]/@value'
        hid_xnxq_xpath = '//*[@id="hidXNXQ"]/@value'
        html = etree.HTML(self.html_module_index)
        view_state = html.xpath(view_state_xpath)[0]
        view_validation = html.xpath(view_validation_xpath)[0]
        hid_xnxq = html.xpath(hid_xnxq_xpath)[0]
        # hid_xnxq = '2019-20202'
        # 有无余量
        ywyl_dict = {
            '有': '%D3%D0',
            '无': '%CE%DE'
        }
        query_class_by_num_payload = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '_LASTFOCUS': '',
            '__VIEWSTATE': view_state,
            '__EVENTVALIDATION': view_validation,
            'ddl_kcxz': '',
            'ddl_ywyl': ywyl_dict[self.ywyl],
            'ddl_kcgs': '',
            'ddl_xqbs': '1',
            'ddl_sksj': '',
            'TextBox1': '',
            # 'Button2': '%C8%B7%B6%A8',
            'txtYz': '',
            'hidXNXQ': hid_xnxq
        }
        # 将字典转换为键值对字符串
        query = []
        for item in query_class_by_num_payload.items():
            query.append('='.join(item))
        query = '&'.join(query)
        return query

    @staticmethod
    def get_html(url, headers=None) -> str:
        response = requests.get(url, headers=headers)
        assert response.status_code == 200
        html = response.text
        return html


if __name__ == '__main__':
    username = input('username: ')
    password = input('password: ')
    query_class = QueryClass(username, password)
    module_url = query_class.module_url
    query_class.get_class_info()
