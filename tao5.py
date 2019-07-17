# -*- coding: utf-8 -*- 
"""
     @Time : 2019/7/15 15:14 
     @Author : lanzhao_ma 
     @File : tao5.py 
"""


import asyncio
import time, random
from pyppeteer.launcher import launch  # 控制模拟浏览器用
from retrying import retry  # 设置重试次数用的
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import pymysql
from tao_settings import *


width, height = 1366, 768
t1 = random.uniform(3, 5)#设置每次睡眠的时间为随机

async def main(username, pwd, url):  # 定义main协程函数，
    # 以下使用await 可以针对耗时的操作进行挂起'args': ['--no-sandbox'],
    browser = await launch({'headless': False, 'args': ['--no-sandbox']})  # 启动pyppeteer 属于内存中实现交互的模拟器
    page = await browser.newPage()  # 启动个新的浏览器页面
    #width, height = screen_size()
    print('启动个新的浏览器页面')
    await page.setViewport({
        "width": width,
        "height": height
    })
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')

    await page.goto(url)  # 访问登录页面
    # 替换淘宝在检测浏览时采集的一些参数。
    # 就是在浏览器运行的时候，始终让window.navigator.webdriver=false
    # navigator是windiw对象的一个属性，同时修改plugins，languages，navigator 且让

    await page.evaluate(
        '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    # 使用type选定页面元素，并修改其数值，用于输入账号密码，修改的速度仿人类操作，因为有个输入速度的检测机制
    # 因为 pyppeteer 框架需要转换为js操作，而js和python的类型定义不同，所以写法与参数要用字典，类型导入
    await page.evaluate('''document.getElementById("J_Quick2Static").click()''')
    time.sleep(t1)
    #增加测试
    await page.evaluate('''document.getElementById("J_SubmitStatic").click()''')
    time.sleep(t1)

    await page.type('.J_UserName', username, {'delay': input_time_random() - 50})
    await page.type('#J_StandardPwd input', pwd, {'delay': input_time_random()})

    # await page.screenshot({'path': './headless-test-result.png'})    # 截图测试
    time.sleep(t1)


    # 检测页面是否有滑块。原理是检测页面元素。
    slider = await page.Jeval('#nocaptcha', 'node => node.style')  # 是否有滑块

    if slider:
        print('当前页面出现滑块')
        await page.screenshot({'path': './headless-login-slide.png'}) # 截图测试
        flag, page = await mouse_slide(page=page)  # js拉动滑块过去。
        time.sleep(t1)
        if flag:
            await page.keyboard.press('Enter')  # 确保内容输入完毕，少数页面会自动完成按钮点击
            print("print enter", flag)
            await page.evaluate('''document.getElementById("J_SubmitStatic").click()''')  # 如果无法通过回车键完成点击，就调用js模拟点击登录按钮。

            time.sleep(t1)
            # cookies_list = await page.cookies()
            # print(cookies_list)
            await get_cookie(page)  # 导出cookie 完成登陆后就可以拿着cookie玩各种各样的事情了。
    else:

        print("")
        await page.keyboard.press('Enter')
        print("print enter")
        time.sleep(t1)

        #出现错误的处理
        #await page.type('#J_StandardPwd input', pwd, {'delay': input_time_random()})
        #await page.screenshot({'path': './headless-login-slide.png'})  # 截图测试
        #flag, page = await mouse_slide(page=page)  # js拉动滑块过去。
        #time.sleep(5)

        await page.keyboard.press('Enter')  # 确保内容输入完毕，少数页面会自动完成按钮点击
        # print("print enter", flag)
        # await page.evaluate('''document.getElementById("J_SubmitStatic").click()''')  # 如果无法通过回车键完成点击，就调用js模拟点击登录按钮。

        #time.sleep(10)
        # cookies_list = await page.cookies()
        # print(cookies_list)
        # while True:
        #     ele = await page.J("J_SiteNavSeller")  # 如果元素不存在，ele=None
        #     if ele:
        #         await page.click("J_SiteNavSeller", {'delay': input_time_random() + 300})
        #         await page.waitForNavigation({'waitUntil': 'load'})
        #     else:
        #         break

    print('进入淘宝')
    #await page.evaluate('''document.getElementById("J_SiteNavSeller").click()''')
    await get_cookie(page)  # 导出cookie 完成登陆后就可以拿着cookie玩各种各样的事情了。
    #ele = await page.goto('https://myseller.taobao.com/home.htm')
    # 将界面拉倒底
    # await page.evaluate("() => {window.scrollBy(0, document.body.scrollHeight)}")
    # await page.waitFor(1000)


    time.sleep(t1)
    baby_info=[]
    for i in range(START,END):
        print('第{}页'.format(i))
        await get_data(page,baby_info)
        content = await page.content()
        soup = BeautifulSoup(content, 'lxml')
        next_page = soup.find_all('div', attrs={"data-reactid": ".0.5.0.2"})
        ne = next_page[0]

        try:
            n = ne['disabled']
            print('到底')
        except:
            await page.goto('https://trade.taobao.com/trade/itemlist/list_sold_items.htm?action=itemlist%2FSoldQueryAction&event_submit_do_query=1&auctionStatus=SUCCESS&tabCode=success&pageNum={0}'.format(i+1))
            time.sleep(t1)
    if len(baby_info)==0:
        print('没有新数据')
        news_nodata={}
        news_nodata['订单号'] = '没有确认的新订单'
        news_nodata['时间'] = '没有确认的新订单'
        news_nodata['宝贝名称'] = '没有确认的新订单'
        news_nodata['单价'] = '没有确认的新订单'
        news_nodata['购买数量'] = '没有确认的新订单'
        news_nodata['买家昵称'] = '没有确认的新订单'
        news_nodata['实收款'] = '没有确认的新订单'
        news_nodata['评价情况'] = '没有确认的新订单'
        baby_info.append(pd.DataFrame(news_nodata, index=[0]))
    else:
        print('有数据')
        #baby_info.append(pd.DataFrame(news_data, index=[0]))
    await Write_info(baby_info)
    time.sleep(10)
    await page.close()
    time.sleep(t1)
    await browser.close()

        # await page.waitFor(20)
        # await page.waitForNavigation()
        # time.sleep(10)

        # try:
        #     global error  # 检测是否是账号密码错误
        #     print("error_1:", error)
        #     error = await page.Jeval('.error', 'node => node.textContent')
        #     print("error_2:", error)
        # except Exception as e:
        #     error = None
        # finally:
        #     if error:
        #         print('确保账户安全重新入输入')
        #         # 程序退出。
        #         loop.close()
        #     else:
        #         print(page.url)
        #         #await get_cookie(page)


    #time.sleep(100)

#import pymysql

# 用来操作数据库的类
# class MySQLCommand(object):
#     # 类的初始化
#     def __init__(self):
#         self.host = 'localhost'
#         self.port = 3306  # 端口号
#         self.user = 'root'  # 用户名
#         self.password = "123456"  # 密码
#         self.db = "taobao_info"  # 库
#         self.table = "taobao_list"  # 表
#
#     # 链接数据库
#     def connectMysql(self):
#         try:
#             self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user,
#                                         passwd=self.password, db=self.db, charset='utf8')
#             self.cursor = self.conn.cursor()
#         except:
#             print('connect mysql error.')

    # 插入数据，插入之前先查询是否存在，如果存在就不再插入
async def insertData(baby_info,data_tb,news_data):

    host = 'localhost'
    port = 3306  # 端口号
    user = 'root'  # 用户名
    password = "123456"  # 密码
    db = "taobao_info"  # 库
    table = "baby_list"  # 表
    conn = pymysql.connect(host=host, port=port, user=user,
                           passwd=password, db=db, charset='utf8')
    cursor = conn.cursor()
    #table = "taobao_list"  # 要操作的表格
    # 注意，这里查询的sql语句url=' %s '中%s的前后要有空格
    #print('正在插入数据')
    #在数据库将or_id设为主键
    sqlExit = "SELECT DISTINCT baby_list.or_id FROM baby_list WHERE baby_list.or_id = ' %s '" % (data_tb['订单号'])
    #cursor = conn.cursor()
    #print('判断是否查到')
    res = cursor.execute(sqlExit)
    if res:  # res为查询到的数据条数如果大于0就代表数据已经存在
        print("数据已存在", res)
        #return 0
    # 数据不存在才执行下面的插入操作
    else:
        try:
            sql = "INSERT INTO baby_list (or_id,creat_time,baby_name,unit_price,baby_number,purchaser_name,proceeds,is_estimate) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')" % (data_tb['订单号'],data_tb['时间'],data_tb['宝贝名称'],data_tb['单价'],data_tb['购买数量'],data_tb['买家昵称'],data_tb['实收款'],data_tb['评价情况'])

            result = cursor.execute(sql)
            print('开始提交')
            conn.commit()
            print('提交')
            if result:
                news_data['订单号'] = data_tb['订单号']
                news_data['时间'] = data_tb['时间']
                news_data['宝贝名称'] = data_tb['宝贝名称']
                news_data['单价'] = data_tb['单价']
                news_data['购买数量'] = data_tb['购买数量']
                news_data['买家昵称'] = data_tb['买家昵称']
                news_data['实收款'] = data_tb['实收款']
                news_data['评价情况'] = data_tb['评价情况']

                baby_info.append(pd.DataFrame(news_data, index=[0]))
                print(news_data)
            else:
                print('没有新订单')
        except:
            print('没有新订单')


async def Write_info(baby_info):

    table_name = datetime.datetime.now().strftime('%Y-%m-%d')
    pd.concat(baby_info, ignore_index=True, sort=True).to_excel(r'C:\Users\Administrator\Desktop\taobao_info_{}.xlsx'.format(table_name))

async def page_evaluate(page):
    # 替换淘宝在检测浏览时采集的一些参数。
    # 就是在浏览器运行的时候，始终让window.navigator.webdriver=false
    # navigator是windiw对象的一个属性，同时修改plugins，languages，navigator
    await page.evaluate('''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => undefined } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

async def get_data(page,baby_info):


    content = await page.content()

    soup = BeautifulSoup(content, 'lxml')
    lilist = soup.find_all('div', attrs={"class": "item-mod__trade-order___2LnGB trade-order-main"})
    for li in lilist:
        data_tb = {}
        news_data = {}
        data_r = li['data-reactid']
        id = li['data-reactid'][-18:]  # 订单号
        data_rea_time = '{}.0.1.0.0.0.6'.format(data_r)
        creat_time = li.find('span', {'data-reactid': data_rea_time}).get_text()  # 时间
        data_rea_name = '{}.1.1.$0.$0.0.1.0.0.1'.format(data_r)
        baby_name = li.find('span', {'data-reactid': data_rea_name}).get_text()  # 宝贝名称
        data_rea_price = '{}.1.1.$0.$1.0.1.1'.format(data_r)
        unit_price = li.find('span', {'data-reactid': data_rea_price}).get_text()  # 单价
        data_rea_number = '{}.1.1.$0.$2.0.0'.format(data_r)
        baby_number = li.find('p', {'data-reactid': data_rea_number}).get_text()  # 购买数量
        data_rea_purchaser = '{}.1.1.$0.$4.0.0.0'.format(data_r)
        purchaser_name = li.find('a', {'data-reactid': data_rea_purchaser}).get_text()  # 买家昵称
        data_rea_proceeds = '{}.1.1.$0.$6.0.0.2.0.1'.format(data_r)
        proceeds = li.find('span', {'data-reactid': data_rea_proceeds}).get_text()  # 实收款
        data_rea_estimate = '{}.1.1.$0.$7.0.$0.0'.format(data_r)
        try:
            is_estimate = li.find('a', {'data-reactid': data_rea_estimate}).get_text()  # 评价情况
        except:
            is_estimate = '都未评价'

        data_tb['订单号'] = id
        data_tb['时间'] = creat_time
        data_tb['宝贝名称'] = baby_name
        data_tb['单价'] = unit_price
        data_tb['购买数量'] = baby_number
        data_tb['买家昵称'] = purchaser_name
        data_tb['实收款'] = proceeds
        data_tb['评价情况'] = is_estimate
        await insertData(baby_info,data_tb,news_data)


        #baby_info.append(pd.DataFrame(data_tb, index=[0]))
        #print("=" * 50)


# 获取登录后cookie
async def get_cookie(page):
    # res = await page.content()
    cookies_list = await page.cookies()
    cookies = ''
    for cookie in cookies_list:
        str_cookie = '{0}={1};'
        str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
        cookies += str_cookie
    print(cookies)
    return cookies


def retry_if_result_none(result):
    return result is None


@retry(retry_on_result=retry_if_result_none, )
async def mouse_slide(page=None):
    await asyncio.sleep(2)
    try :
        #鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
        await page.hover('#nc_1_n1z') # 不同场景的验证码模块能名字不同。
        await page.mouse.down()
        await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})
        await page.mouse.up()
    except Exception as e:
        print(e, ':验证失败')
        return None,page
    else:
        await asyncio.sleep(2)
        # 判断是否通过
        slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')
        if slider_again != '验证通过':
            return None,page
        else:
            #await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
            print('验证通过')
            return 1,page


def input_time_random():
    return random.randint(100, 151)


if __name__ == '__main__':
    for user in USER.keys():
        username = user  # 淘宝用户名
        pwd = USER[user]  # 密码
        #print(username,pwd)
    #url = 'https://login.taobao.com/member/login.jhtml?style=mini&css_style=b2b&from=b2b&full_redirect=true&redirect_url=https://login.1688.com/member/jump.htm?target=https://login.1688.com/member/marketSigninJump.htm?Done=http://login.1688.com/member/taobaoSellerLoginDispatch.htm&reg= http://member.1688.com/member/join/enterprise_join.htm?lead=http://login.1688.com/member/taobaoSellerLoginDispatch.htm&leadUrl=http://login.1688.com/member/'
    #url = 'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d94GYIMP&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2f'
    #url = 'https://myseller.taobao.com/home.htm'
        url = 'https://trade.taobao.com/trade/itemlist/list_sold_items.htm?action=itemlist/SoldQueryAction&event_submit_do_query=1&auctionStatus=SUCCESS&tabCode=success&pageNum=1'
        loop = asyncio.get_event_loop()  # 协程，开启个无限循环的程序流程，把一些函数注册到事件循环上。当满足事件发生的时候，调用相应的协程函数。
        loop.run_until_complete(main(username, pwd, url))  # 将协程注册到事件循环，并启动事件循环
    # except:
    #     loop = asyncio.get_event_loop()  # 协程，开启个无限循环的程序流程，把一些函数注册到事件循环上。当满足事件发生的时候，调用相应的协程函数。
    #     loop.run_until_complete(main(username, pwd, url))  # 将协程注册到事件循环，并启动事件循环