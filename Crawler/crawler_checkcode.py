import time
import random
from Crawler.get_checkcode import *

count = 100
for i in range(count):
    get_checkcode(save=True, filepath='../image/images_source')
    print('√')
    time.sleep(random.random())
