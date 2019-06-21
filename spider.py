# encoding: utf-8

import requests
from bs4 import BeautifulSoup
import json
import time
#import scrapy
#import scrapy


# BASE_URLS = 'https://www.lagou.com/zhaopin/Python/{0}/?filterOption=3'
# PAGE_URL_LIST = []
# for i in range(1,31):
#     if i == 1:
#         url = 'https://www.lagou.com/zhaopin/Python/?labelWords=label'
#     else:
#         url = BASE_URLS.format(i)
#     PAGE_URL_LIST.append(url)

def parse_page(url):
    headers = {
        'Connection': 'keep-alive',
        'Cache - Control': 'max - age = 0',
        'Accept - Language': 'zh - CN, zh;q = 0.9',
        'Host': 'www.lagou.com',
        'Content - Length': '25',
        'Origin': 'https://www.lagou.com',
        'Content - Type': 'application / x - www - form - urlencoded;charset = UTF - 8',
        'Referer': 'https://www.lagou.com/zhaopin/Python/2/?filterOption=3',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Anit-Forge-Cod': '0',
        'X - Anit - Forge - Token': 'None',
        'X - Requested - With': 'XMLHttpRequest',
        'user-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        'cookie':"user_trace_token=20190603150559-1cb264c2-f3d1-421b-8dea-fb4ec0cb5b2f; _ga=GA1.2.1052770785.1559545543; _gat=1; LGUID=20190603150559-0a927347-85ce-11e9-a93d-525400f775ce; JSESSIONID=ABAAABAABEEAAJA7BBF5CEB2B86F25866A0E5BC8889A6CE; _gid=GA1.2.322551655.1559545547; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1559545543,1559545547; LGSID=20190603150604-0d2fed2b-85ce-11e9-a93d-525400f775ce; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DpIGTxQjW1xz1Q0_LyKQ4BtVPNmYIGczDt4QBGG9Rp3C%26wd%3D%26eqid%3Da022421e0005549a000000045cf4c6d4; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%8C%97%E4%BA%AC; TG-TRACK-CODE=index_code; X_HTTP_TOKEN=b0f517a37fd6d2ad9665459551c9488426aa502f01; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1559545653; LGRID=20190603150749-4bfb60db-85ce-11e9-a1c2-5254005c3644"
        }
    data = {
        'first': 'true',
        'pn': '1',
        'kd': 'Python',
    }
    response = requests.post(url, headers=headers, data=data)
    #text = response.text
    text = response.content.decode('utf-8')
    #response.text是自动识别解码，可能会出现乱码, 所可以手动指定解码方式response.content.decode('utf-8')
    soup = BeautifulSoup(text,'lxml')
    print(soup)
    lis = soup.findAll('li', attrs={'class':'con_list_item default_list'})
    for li in lis:
        gz = {}
        name = li['data-positionname']
        gongzi = li.find('span', attrs = {'class':'money'}).text.strip()
        yaoqiu = li.find('div', attrs = {'class':'li_b_l'}).text.strip()
        company = li.find('div', attrs = {'class':'company_name'}).text.strip()
        jineng = li.find('div', attrs = {'class':'li_b_l'}).text.strip()
        href = li.find('a', attrs = {'class':'position_link'})['href']
        gz['name'] = name
        gz['gongzi'] = gongzi
        gz['company'] = company
        gz['jineng'] = jineng
        gz['href'] = href
        gz['yaoqiu'] = yaoqiu
        print(gz)



    # conMidtab = soup.find('div', attrs={"class":"conMidtab"})
    # tables = conMidtab.find_all("table")
    # ty = []


    # for t in tables:
    #
    #     trs = t.find_all('tr')[2:]
    #     for tr in trs:
    #         lis = {}
    #         tds = tr.find_all('td')
    #         city_td = tds[0]
    #         city = list(city_td.stripped_strings)[0]#stripped_strings节点生产器，可以获得所有子孙标签
    #
    #         temp_td = tds[-2]
    #         min_temp = list(temp_td.stripped_strings)[0]
    #         lis['城市']=city
    #         lis['最低气温']=min_temp
    #         ty.append(lis)
    #     return ty



def save_data(data):

    with open('ban.json','w',encoding='utf-8') as f:
# json.dump作用  encoding指定打开的编码格式
#将字典、列表dump成满足json格式的字符串
        json.dump(data,f,ensure_ascii=False) #将ascii定为False







def main():
    #for ur in PAGE_URL_LIST:

    url = 'https://www.lagou.com/zhaopin/Python/2/?filterOption=3'
    ty = parse_page(url)
    #print("="*30)
    #time.sleep(8)

    #save_data(ty)


if __name__ == '__main__':
    main()
