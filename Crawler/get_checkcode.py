import os
import hashlib
import requests


def get_md5(content: bytes):
    """获取md5值"""
    md5_obj = hashlib.md5()
    md5_obj.update(content)
    hash = md5_obj.hexdigest()
    return hash


def get_checkcode(*, save=True, filepath='../image/images_source', filename=None):
    url = 'http://jxgl.hdu.edu.cn/CheckCode.aspx'
    response = requests.get(url)
    content = response.content
    if save:
        if filename is None:
            filename = get_md5(content)
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        with open('/'.join((filepath, filename)) + '.gif', 'wb') as fp:
            fp.write(content)
    return content
