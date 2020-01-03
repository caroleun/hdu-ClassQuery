# -*- coding: utf-8 -*-
import random
import os
from io import BytesIO
from collections import defaultdict
from PIL import Image
import pytesseract
from Crawler.get_checkcode import get_md5


def get_threshold(image) -> int:
    """获取图片中像素点数量最多的像素"""
    # 灰度: 数量
    pixel_dict = defaultdict(int)
    width, height = image.size
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            pixel_dict[pixel] += 1
    count_max = max(pixel_dict.values())
    # 转置pixel_dict
    pixel_dict_reverse = {v: k for k, v in pixel_dict.items()}
    threshold = pixel_dict_reverse[count_max]
    return threshold


def get_bin_table(image: Image):
    """通过阈值生成灰度值转二值的映射table"""
    threshold = get_threshold(image)
    border_threshold = get_border_threshold(image)
    table = []
    for i in range(256):
        # 适当的范围
        rate = 0.1
        if threshold * (1 - rate) <= i <= threshold * (1 + rate):
            table.append(1)
        else:
            table.append(0)
    for threshold in border_threshold:
        table[threshold] = 1 if table[threshold] == 0 else 1
    return table


def get_border_threshold(image: Image) -> set:
    """获取图片边框的像素(灰度)值"""
    thresholds = set()
    width, height = image.size
    for x in range(width):
        pixel_start = image.getpixel((x, 0))
        pixel_end = image.getpixel((x, height - 1))
        thresholds.add(pixel_start)
        thresholds.add(pixel_end)
    for y in range(height):
        pixel_start = image.getpixel((0, y))
        pixel_end = image.getpixel((width - 1, y))
        thresholds.add(pixel_start)
        thresholds.add(pixel_end)
    return thresholds


def cut_noise(image):
    """去除图片中的噪声点"""
    width, height = image.size
    # 噪声点的位置
    change_pos = []
    # 去除边框: 0和size-1
    for x in range(width):
        for y in range(height):
            # 边框
            if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                change_pos.append((x, y))
                continue
            '''
            # 用来记录该点附近黑色像素的数量
            noise_num = 0
            # 遍历这个点周围的九宫格
            for x_ in range(x - 1, x + 2):
                for y_ in range(y - 1, y + 2):
                    if image.getpixel((x_, y_)) != 1:   # 1为白色，0为黑色
                        noise_num += 1
            # 如果九宫格内黑色像素数量<=4, 则判断为噪声
            if noise_num <= 4:
                change_pos.append((x, y))
            '''
    # 将噪声点像素改为1(白色)
    for pos in change_pos:
        image.putpixel(pos, 1)
    return image


def ocr_img(image: Image) -> str:
    # 转化为灰度图
    image = image.convert('L')
    # 出现最多的像素
    # max_pixel = get_threshold(image)
    # 二值化
    table = get_bin_table(image)
    image = image.point(table, '1')     # 噪点全部转换成白色
    # 去噪点
    image = cut_noise(image)
    # image.show()

    image = image.convert('L')  # 这一步必须...
    # 识别图片中的数字和字母
    try:
        # text = pytesseract.image_to_string(image, lang='eng', config='digits')  # config='digits'仅识别图片中的数字
        text = pytesseract.image_to_string(image,
                                           config='result -psm 6 digits').strip()
    except Exception as e:
        # image.save(f'image/images_ocr_failed/{get_md5(image.tobytes())}.gif')
        raise Exception('验证码识别失败')
    else:
        # 去除特殊字符
        exclude_char_list = ' .:\\|\'\"?![],()~@#$%^&*_-+={};<>/'
        text = ''.join([x for x in text if x not in exclude_char_list])
        # image.save(f'image/images_ocr_success/{text}.gif')
    return text


def train(count: int = -1):
    """识别images_source目录下的验证码，并保存到images_mark"""
    import shutil
    images = os.listdir('image/images_source')
    if count < 0:
        count = len(images)
    for i in range(count):
        image_name = images[i]
        image_path = f'image/images_source/{image_name}'
        image = Image.open(image_path).convert('1')
        text = ocr_img(image)
        print(text)
        shutil.copy(image_path, f'image/images_mark/{text}.gif')


if __name__ == '__main__':
    train()
