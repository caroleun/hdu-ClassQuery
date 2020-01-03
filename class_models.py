# -*- coding: utf-8 -*-
import re
import requests


class Modules:
    def __init__(self, username: str, cookie: str):
        self.username = username
        self.url_index = 'http://jxgl.hdu.edu.cn/xs_main.aspx?xh=' + self.username
        self.cookie = cookie
        self.html = ''
        self.modules = self.get_index()
        # self.体育课 = self.get_model_url('选体育课')
        # self.通识选修课 = self.get_model_url('通识选修课')

    def get_index(self) -> list:
        response = requests.get(self.url_index, headers={'Cookie': self.cookie})
        self.html = response.text
        pattern_li = re.compile(
            "<li><a href=['\"]([^#]+?)['\"] target=['\"].+?['\"] onclick=['\"].+?;['\"]>(.+?)</a></li>"
        )
        results = re.findall(pattern_li, self.html)
        modules = [('http://jxgl.hdu.edu.cn/' + x[0], x[1]) for x in results]
        return modules
        # 选普通理论及实验课
        # 选体育课
        # 选实践课
        # 通识选修课
        # 学生选课情况查询
        # 网上报名
        # 理论教学质量评价
        # 实验实践教学质量评价
        # 专业推荐课表查询
        # 学生个人课表
        # 学生考试查询
        # 成绩查询
        # 等级考试查询
        # 培养计划
        # 学生补考查询
        # 学生选课情况查询
        # 学生课程替代查询
        # 学生选题查询
        # 学生选题
        # 个人信息
        # 教务公告

    def get_module_url(self, item: str) -> str:
        """在self.models中查找指定模块的url
        :return: url: str"""
        for model in self.modules:
            if model[1] == item:
                return model[0]


if __name__ == '__main__':
    username = '18151536'
    cookie = 'ASP.NET_SessionId= path=/; HttpOnly, route=;Path=/'
    cookie = 'ASP.NET_SessionId=ldi5ng45e5sgev554dwoosma; route=8d6cef81efff9b6a4d8532c8c2684b46'
    my_models = Modules(username, cookie)
    models = my_models.modules
    print(models)
