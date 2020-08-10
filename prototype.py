# import bs4 as BeautifulSoup
# import requests

# url = 'http://www.cde.org.cn/transparent.do?method=yzxpjSpxlList&taskType=xb'
# headers = {
#             "Host": "www.cde.org.cn",
#             "Origin": "http://www.cde.org.cn",
#             "Referer": "http://www.cde.org.cn/transparent.do?method=yzxpjSpxlList",
#             "Upgrade-Insecure-Requests": "1",
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
#             "X-Requested-With": "XMLHttpRequest"
# }
# data = {
    
# }
# response = requests.get(url=url, data=data, headers=headers, timeout=30)
# print(response)
# print(response.text)

# from selenium import webdriver 
# import time

# url = 'http://www.cde.org.cn/news.do?method=news_index_yzxpj'
# driver = webdriver.Chrome() # 声明调用Chrome
# driver.get(url) # 打开网页
# time.sleep(20)  # 等待3s




# driver.close()#浏览器可以同时打开多个界面，close只关闭当前界面，不退出浏览器
# driver.quit()#退出整个浏览器

import webbrowser
import browsercookie
import requests
import os
import json
import base64
import sqlite3
from win32crypt import CryptUnprotectData
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# import urllib
import time
import random
import xlwt
# import urllib.request
from bs4 import BeautifulSoup


# https://blog.csdn.net/pyyong2011/article/details/105045883
# 实现从浏览器中获取Cookies
def get_string(local_state):
    with open(local_state, 'r', encoding='utf-8') as f:
        s = json.load(f)['os_crypt']['encrypted_key']
    return s

def pull_the_key(base64_encrypted_key):
    encrypted_key_with_header = base64.b64decode(base64_encrypted_key)
    encrypted_key = encrypted_key_with_header[5:]
    key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return key

def decrypt_string(key, data):
    nonce, cipherbytes = data[3:15], data[15:]
    aesgcm = AESGCM(key)
    plainbytes = aesgcm.decrypt(nonce, cipherbytes, None)
    plaintext = plainbytes.decode('utf-8')
    return plaintext

def get_cookie_from_chrome(host: 'www.cde.org.cn'):
    local_state = os.environ['LOCALAPPDATA'] + r'\Google\Chrome\User Data\Local State'
    cookie_path = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Default\Cookies"
    
    sql = "select host_key,name,encrypted_value from cookies where host_key='%s'" % host

    with sqlite3.connect(cookie_path) as conn:
        cu = conn.cursor()
        res = cu.execute(sql).fetchall()
        cu.close()
        cookies = {}
        key = pull_the_key(get_string(local_state))
        for host_key, name, encrypted_value in res:
            if encrypted_value[0:3] == b'v10':
                cookies[name] = decrypt_string(key, encrypted_value)
            else:
                cookies[name] = CryptUnprotectData(encrypted_value)[1].decode()

        print("===cookies===:{}".format(cookies))
        return cookies

def check_lamp(td_lamp):
    length = len(td_lamp.contents)
    if length == 1:
        return 1  # 空白 本专业未启动
    elif length == 3:
        if td_lamp.contents[1]["src"] == '/styles/images/lamp_shut.gif':
            return 3  # 灭灯 本专业已完成审评
        elif td_lamp.contents[1]["src"] == '/styles/images/lamp.gif':
            return 2  # 开灯 本专业正在审评 
        else:
            return 9  # 异常
    else:
        return 9 # 异常

def run():
    if input('是否启动浏览器以刷新Cookies？(Y/n)') == 'n':
        pass
    else:
        chromePath = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        url = 'http://www.cde.org.cn/transparent.do?method=yzxpjSpxlList&taskType=xb'
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chromePath))
        webbrowser.get('chrome').open(url)
        print("等待10s使浏览器打开和加载页面，以便抓取Cookies...")
        time.sleep(10)
    

    datalist = []
    # url = 'http://www.cde.org.cn/transparent.do?method=yzxpjSpxlList&taskType=xb'
    url = 'http://www.cde.org.cn/transparent.do?method=yzxpjSpxlList'
    params = {
        "taskType": "xb",
        "acceptid": "",
        "currentPageNumber": "1",
        "pageMaxNumber": "80",
        "totalPageCount": "42",
        "pageroffset": "",
        "pageMaxNum": "80",
        "pagenum": "1"
    }
    print("======param=====:{}".format(params))
    header={
        "Host": "www.cde.org.cn",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Referer": "http://www.cde.org.cn/transparent.do?method=yzxpjSpxlList&taskType=xb",
        "Accept-Language": "zh-CN,zh;q=0.9",
        # "Cookie": ,
        "Connection": "keep-alive"
    }

    cookies = get_cookie_from_chrome(host="www.cde.org.cn")
    response = requests.post(url,data=params,headers=header,cookies=cookies)
    html = response.text
    # print(html)
    if len(html) < 30000:
        print('爬取失败，请求返回异常')
        return 0

    soup = BeautifulSoup(html)
    page_count = int(soup.find("td", id="pageNumber").font.next_sibling.next_sibling.string)
    print('共发现{}页数据，开始逐页进行获取'.format(page_count))

    for pagenum in range(1,(page_count+1)):
        print('开始获取第{}页数据'.format(pagenum))
        wait_time = random.randint(3,8)
        print("等待{}s".format(wait_time))
        time.sleep(wait_time)
        params = {
            "taskType": "xb",
            "acceptid": "",
            "currentPageNumber": str(pagenum),
            "pageMaxNumber": "80",
            "totalPageCount": str(page_count),
            "pageroffset": str(len(datalist)),
            "pageMaxNum": "80",
            "pagenum": str(pagenum)
        }
        print("======param=====:{}".format(params))
        response = requests.post(url,data=params,headers=header,cookies=cookies)
        html = response.text
        # print(html)
        soup = BeautifulSoup(html)
        temp_data_count = len(soup.find_all('tr', {"class": "newsindex"}))
        if temp_data_count == 0:
            print(html)
            continue

        print('本页面共发现{}条数据'.format(temp_data_count))
        try:
            for idx, tr in enumerate(soup.find_all('tr', {"class": "newsindex"})):
                tds = tr.find_all('td')
                datalist.append({
                    '序号': tds[0].string.strip(),
                    '受理号': tds[1].string.strip(),
                    '药品名称': tds[2].string.strip(),
                    '进入中心时间': tds[3].string.strip(),
                    '统计': check_lamp(tds[4]),
                    '药理毒理': check_lamp(tds[5]),
                    '临床': check_lamp(tds[6]),
                    '药学': check_lamp(tds[7]),
                    '备注': tds[8].contents[0].replace('\n', '').replace('\r', '').replace('\t', '').strip(),
                })
        except Exception as e:
            print(e)
            _ = input('check error')
    print('一致性评价数据爬取完毕，共获得数据{}行'.format(len(datalist)))

    workbook = xlwt.Workbook(encoding='utf-8')
    sheet1 = workbook.add_sheet("一致性评价任务{}".format(time.strftime("%Y%m%d",time.localtime()))) 
    # 表格第一行
    sheet1.write(0,0,"一致性评价任务{}".format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())))
    # 表格第二行
    sheet1.write(1,0,"说明，【进入中心时间】~【药学】阶段，数字1表示本专业未启动，数字2表示本专业正在审评")
    # 表格第三行 标题
    header = ['序号','受理号','药品名称','进入中心时间', '统计','药理毒理','临床', '药学','备注']
    for i, head in enumerate(header):
        sheet1.write(2,i,head)
    for i,line in enumerate(datalist):
        for j,head in enumerate(header):
            sheet1.write((3+i),j,line[head])
    workbook.save('一致性.xls')

if __name__ == '__main__':
    run()

    
        



