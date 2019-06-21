# encoding:utf-8
from selenium import webdriver
import urllib
from pyquery import PyQuery as pq
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image
import re,random
import pandas as pd
from openpyxl.workbook import Workbook
from xpinyin import Pinyin
import threading
from selenium.webdriver.chrome.options import Options




# 破解滑动验证

def get_snap(driver):
    '''
    对整个网页截图，保存成图片，然后用PIL.Image拿到图片对象
    :return: 图片对象
    '''
    driver.save_screenshot('full_snap.png')
    page_snap_obj=Image.open('full_snap.png')
    return page_snap_obj


def get_image(driver):
    img = driver.find_element_by_css_selector("[class='gt_box']")
    #img = driver.find_element_by_xpath("html/body/div[10]/div[2]/div[2]/div[2]/div[2]")
    time.sleep(2)
    location = img.location
    size = img.size

    left = location['x']
    top = location['y']
    right = left + size['width']
    bottom = top + size['height']

    page_snap_obj = get_snap(driver)
    image_obj = page_snap_obj.crop((left, top, right, bottom))
    # image_obj.show()
    return image_obj


def get_distance(image1,image2):
    '''
    拿到滑动验证码需要移动的距离
    :param image1:没有缺口的图片对象
    :param image2:带缺口的图片对象
    :return:需要移动的距离
    '''
    threshold=60
    left=59
    for i in range(left,image1.size[0]):
        for j in range(image1.size[1]):
            rgb1=image1.load()[i,j]
            rgb2=image2.load()[i,j]
            res1=abs(rgb1[0]-rgb2[0])
            res2=abs(rgb1[1]-rgb2[1])
            res3=abs(rgb1[2]-rgb2[2])
            if not (res1 < threshold and res2 < threshold and res3 < threshold):
                return i-7 #经过测试，误差为大概为7

def get_tracks(distance):
    distance += 20  # 先滑过一点，最后再反着滑动回来
    v = 0
    t = 0.2
    forward_tracks = []

    current = 0
    mid = distance * 3 / 5
    while current < distance:
        if current < mid:
            a = 2
        else:
            a = -3

        s = v * t + 0.5 * a * (t ** 2)
        v = v + a * t
        current += s
        forward_tracks.append(round(s))

    # 反着滑动到准确位置
    back_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]  # 总共等于-20

    return {'forward_tracks': forward_tracks, 'back_tracks': back_tracks}

def crack(driver):  # 破解滑动认证
    try:
        # 1、点击按钮，得到没有缺口的图片
        button = driver.find_element_by_class_name('gt_refresh_button')
        button.click()
        #time.sleep(5)

        # 2、获取没有缺口的图片
        image1 = get_image(driver)

        # 3、点击滑动按钮，得到有缺口的图片
        button = driver.find_element_by_css_selector("[class='gt_slider_knob gt_show']")
        button.click()
        time.sleep(5)

        # 4、获取有缺口的图片
        image2 = get_image(driver)
        #
        # 5、对比两种图片的像素点，找出位移
        distance = get_distance(image1, image2)
        #print(distance)
        #6、模拟人的行为习惯，根据总位移得到行为轨迹
        tracks = get_tracks(distance)
        # 7、按照行动轨迹先正向滑动，后反滑动
        button = driver.find_element_by_css_selector("[class='gt_slider_knob gt_show']")
        ActionChains(driver).click_and_hold(button).perform()

        # 正常人类总是自信满满地开始正向滑动，自信地表现是疯狂加速
        for track in tracks['forward_tracks']:
            ActionChains(driver).move_by_offset(xoffset=track, yoffset=0).perform()

        # 结果傻逼了，正常的人类停顿了一下，回过神来发现，卧槽，滑过了,然后开始反向滑动
        time.sleep(0.5)
        for back_track in tracks['back_tracks']:
            ActionChains(driver).move_by_offset(xoffset=back_track, yoffset=0).perform()
        else:
            ActionChains(driver).move_by_offset(xoffset=3, yoffset=0).perform()  # 先移过一点
            ActionChains(driver).move_by_offset(xoffset=-3, yoffset=0).perform()  # 再退回来，是不是更像人了

        time.sleep(0.5)  # 0.5秒后释放鼠标
        ActionChains(driver).release().perform()
        time.sleep(5)
        button1 = driver.find_element_by_css_selector("[class='gt_slider_knob gt_show']")
        if button1:
            return False
    except:
        return True



def login_tianyanchan(url,phone,password):  # 启动加登录

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')


    driver = webdriver.Chrome(executable_path='chromedriver',options=chrome_options)

    #driver.maximize_window()#将浏览器最大化
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    time.sleep(10)


    driver.find_element_by_xpath(".//*[@id='web-content']/div/div[2]/div/div[2]/div/div[3]/div[1]/div[2]").send_keys(
        Keys.ENTER)
    print('1')
    time.sleep(3)
    driver.find_element_by_xpath(
        ".//*[@id='web-content']/div/div[2]/div/div[2]/div/div[3]/div[2]/div[2]/input").send_keys(phone)
    driver.find_element_by_xpath(
        ".//*[@id='web-content']/div/div[2]/div/div[2]/div/div[3]/div[2]/div[3]/input").send_keys(password)
    driver.find_element_by_xpath(".//*[@id='web-content']/div/div[2]/div/div[2]/div/div[3]/div[2]/div[5]").click()
    time.sleep(5)

    longin = crack(driver)

    if longin==False:
        for i in range(4):
            longin = crack(driver)
            if longin==True:
                break
    else:
        time.sleep(20) # #睡时间长一点，让其登陆成功。

    return driver

def CompanyInfo(driver):  # 开始抓取数据

    t1 = random.uniform(8, 10)
    t2 = random.uniform(3, 5)
    print('正在打印第1页')

    company_list = driver.find_elements_by_xpath('.//div[contains(@class, "content")]')[32:52]  # 获取当前页面所有公司的div
    company_info = []
    for company in company_list:
        com = {}
        com_info = []
        com['公司名称'] = company.text.split('\n')[0]
        c = company.text.split('\n')
        for e in c:
            f = re.findall('：', e)
            if f:
                com_info.append(e)
        if len(com_info) == 5:
            com['法定代表人'] = com_info[0].split('：')[1]
            com['注册资本'] = com_info[1].split('：')[1]
            com['成立日期'] = com_info[2].split('：')[1]
            com['电话'] = com_info[3].split('：')[1].split('查')[0]
            com['邮箱'] = com_info[4].split('：')[1].split('查')[0]

        elif len(com_info) == 4:
            if re.findall('电话', company.text):
                com['法定代表人'] = com_info[0].split('：')[1]
                com['注册资本'] = com_info[1].split('：')[1]
                com['成立日期'] = com_info[2].split('：')[1]
                com['电话'] = com_info[3].split('：')[1].split('查')[0]
            else:
                com['法定代表人'] = com_info[0].split('：')[1]
                com['注册资本'] = com_info[1].split('：')[1]
                com['成立日期'] = com_info[2].split('：')[1]
                com['邮箱'] = com_info[3].split('：')[1].split('查')[0]

        elif len(com_info) == 3:
            com['法定代表人'] = com_info[0].split('：')[1]
            com['注册资本'] = com_info[1].split('：')[1]
            com['成立日期'] = com_info[2].split('：')[1]
        # print(com)

        # return com
        company_info.append(pd.DataFrame(com, index=[0]))

        # pd.concat(company_info,ignore_index=True,sort=True).to_excel('company_info.xlsx')

    time.sleep(t2)
    driver.find_element_by_xpath(".//*[@id='web-content']/div/div[1]/div[2]/div[3]/div/ul/li[12]/a").send_keys(
        Keys.ENTER)
    time.sleep(t1)
    print('=' * 50)

    # 第2，3，4，5页
    for i in range(4):
        print('正在打印第{}页'.format(i + 2))

        company_list = driver.find_elements_by_xpath('.//div[contains(@class, "content")]')[32:52]  # 获取当前页面所有公司的div
        com = {}

        for company in company_list:
            com_info = []
            com['公司名称'] = company.text.split('\n')[0]
            c = company.text.split('\n')
            for e in c:
                f = re.findall('：', e)
                if f:
                    com_info.append(e)
            if len(com_info) == 5:
                com['法定代表人'] = com_info[0].split('：')[1]
                com['注册资本'] = com_info[1].split('：')[1]
                com['成立日期'] = com_info[2].split('：')[1]
                com['电话'] = com_info[3].split('：')[1].split('查')[0]
                com['邮箱'] = com_info[4].split('：')[1].split('查')[0]

            elif len(com_info) == 4:
                if re.findall('电话', company.text):
                    com['法定代表人'] = com_info[0].split('：')[1]
                    com['注册资本'] = com_info[1].split('：')[1]
                    com['成立日期'] = com_info[2].split('：')[1]
                    com['电话'] = com_info[3].split('：')[1].split('查')[0]
                else:
                    com['法定代表人'] = com_info[0].split('：')[1]
                    com['注册资本'] = com_info[1].split('：')[1]
                    com['成立日期'] = com_info[2].split('：')[1]
                    com['邮箱'] = com_info[3].split('：')[1].split('查')[0]

            elif len(com_info) == 3:
                com['法定代表人'] = com_info[0].split('：')[1]
                com['注册资本'] = com_info[1].split('：')[1]
                com['成立日期'] = com_info[2].split('：')[1]
            # print(com)
            company_info.append(pd.DataFrame(com, index=[0]))
        print('=' * 50)

        # pd.concat(company_info, ignore_index=True, sort=True).to_excel('company_info.xlsx')

        time.sleep(t2)
        driver.find_element_by_xpath(".//*[@id='web-content']/div/div[1]/div[2]/div[3]/div/ul/li[13]/a").send_keys(
            Keys.ENTER)
        time.sleep(t1)

    # # 第6页到（倒数第5页）
    # for i in range(5):
    #     print('正在打印第{}页'.format(i + 6))
    #
    #     company_list = driver.find_elements_by_xpath('.//div[contains(@class, "content")]')[32:52]  # 获取当前页面所有公司的div
    #     com = {}
    #     for company in company_list:
    #         com_info = []
    #         com['公司名称'] = company.text.split('\n')[0]
    #         c = company.text.split('\n')
    #         for e in c:
    #             f = re.findall('：', e)
    #             if f:
    #                 com_info.append(e)
    #         if len(com_info) == 5:
    #             com['法定代表人'] = com_info[0].split('：')[1]
    #             com['注册资本'] = com_info[1].split('：')[1]
    #             com['成立日期'] = com_info[2].split('：')[1]
    #             com['电话'] = com_info[3].split('：')[1].split('查')[0]
    #             com['邮箱'] = com_info[4].split('：')[1].split('查')[0]
    #
    #         elif len(com_info) == 4:
    #             if re.findall('电话', company.text):
    #                 com['法定代表人'] = com_info[0].split('：')[1]
    #                 com['注册资本'] = com_info[1].split('：')[1]
    #                 com['成立日期'] = com_info[2].split('：')[1]
    #                 com['电话'] = com_info[3].split('：')[1].split('查')[0]
    #             else:
    #                 com['法定代表人'] = com_info[0].split('：')[1]
    #                 com['注册资本'] = com_info[1].split('：')[1]
    #                 com['成立日期'] = com_info[2].split('：')[1]
    #                 com['邮箱'] = com_info[3].split('：')[1].split('查')[0]
    #
    #         elif len(com_info) == 3:
    #             com['法定代表人'] = com_info[0].split('：')[1]
    #             com['注册资本'] = com_info[1].split('：')[1]
    #             com['成立日期'] = com_info[2].split('：')[1]
    #         # print(com)
    #         company_info.append(pd.DataFrame(com, index=[0]))
    #     print('=' * 50)
    #
    #     #pd.concat(company_info, ignore_index=True, sort=True).to_excel('company_info.xlsx')
    #
    #     time.sleep(t2)
    #     driver.find_element_by_xpath(".//*[@id='web-content']/div/div[1]/div[2]/div[3]/div/ul/li[14]/a").send_keys(
    #         Keys.ENTER)
    #     time.sleep(t1)
    print(company_info)
    return company_info
    #pd.concat(company_info, ignore_index=True, sort=True).to_excel('company_info.xlsx')

def Write_info(company_info,city):

    City = Pinyin().get_pinyin(u"{}".format(city))
    pd.concat(company_info, ignore_index=True, sort=True).to_excel('company_info_{}.xlsx'.format(City))

def url_create(city): # http地址生成
    area = {'河南':'henan','呼和浩特':"hhht",
        '郑州':"zhengzhou",'开封':"kaifeng",'洛阳':"luoyang",'平顶山':"pds",'安阳':"anyang",'鹤壁':"hebi",'焦作':"jiaozuo",'濮阳':"puyang",'许昌':"xuchang",
        '三门峡':"smx",'漯河':"luohe",'南阳':"nanyang",'商丘':"shangqiu",'信阳':"xinyang",'驻马店':"zmd",'新乡':"xinxiang",'济源':"henzx",'周口':"zhoukou",
    }
    ca = area[city]
    BASE_URL = 'https://www.tianyancha.com/login?from=https%3A%2F%2Fwww.tianyancha.com%2Fsearch%3Fbase%3D{}'
    url = BASE_URL.format(ca)
    print(url)
    return url



if __name__=='__main__':
    city = input("请输入城市：")
    url = url_create(city)
    phone='13408467937'
    password = 'kong06031'
    Login = login_tianyanchan(url=url,phone=phone,password=password)
    com = CompanyInfo(Login)
    Write_info(com,city)



