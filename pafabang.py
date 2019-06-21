import requests
from bs4 import BeautifulSoup

def fa_bang_spider(url):

    headers = {
        'Connection': 'keep-alive',
        'Cache - Control': 'max - age = 0',
        'Accept - Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Host': 'lawyer.fabang.com',
        'Upgrade-Insecure-Requests': '1',
        'Accept-Encoding': 'gzip, deflate',

        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'user-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0",
    }
    # data = {
    #     'first': 'true',
    #     'pn': '1',
    #     'kd': 'Python',
    # }
    response = requests.post(url, headers=headers)
    text = response.text
    #text = response.content.decode('utf-8')
    #response.text是自动识别解码，可能会出现乱码, 所可以手动指定解码方式response.content.decode('utf-8')
    soup = BeautifulSoup(text, 'lxml')
    print(soup)
    # lis = soup.findAll('li', attrs={'class': 'con_list_item default_list'})
    # for li in lis:
    #     gz = {}
    #     name = li['data-positionname']
    #     gongzi = li.find('span', attrs={'class': 'money'}).text.strip()
    #     yaoqiu = li.find('div', attrs={'class': 'li_b_l'}).text.strip()
    #     company = li.find('div', attrs={'class': 'company_name'}).text.strip()
    #     jineng = li.find('div', attrs={'class': 'li_b_l'}).text.strip()
    #     href = li.find('a', attrs={'class': 'position_link'})['href']
    #     gz['name'] = name
    #     gz['gongzi'] = gongzi
    #     gz['company'] = company
    #     gz['jineng'] = jineng
    #     gz['href'] = href
    #     gz['yaoqiu'] = yaoqiu
    #     print(gz)


def main():
    #for ur in PAGE_URL_LIST:

    url = 'http://lawyer.fabang.com/list/7516-0-0-key-1-1.html'
    fa_bang_spider(url)



if __name__ == '__main__':
    main()
