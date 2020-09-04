#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   spider.py
@Time    :   2020/07/05 23:54:56
@Desc    :   抓取浏览器Cookies并构造Requests请求，对数据进行抓取。由于CDE反扒机制过于严格，多数情况下无法正常抓取，故放弃本方案
'''
import os
import time
import json
import random
import base64
import sqlite3
import requests
import datetime
import func_timeout
import webbrowser
import browsercookie
from bs4 import BeautifulSoup
from win32crypt import CryptUnprotectData
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class Spider(object):
    def get_string(self, local_state):
        with open(local_state, 'r', encoding='utf-8') as f:
            s = json.load(f)['os_crypt']['encrypted_key']
        return s

    def pull_the_key(self, base64_encrypted_key):
        encrypted_key_with_header = base64.b64decode(base64_encrypted_key)
        encrypted_key = encrypted_key_with_header[5:]
        key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key

    def decrypt_string(self, key, data):
        nonce, cipherbytes = data[3:15], data[15:]
        aesgcm = AESGCM(key)
        plainbytes = aesgcm.decrypt(nonce, cipherbytes, None)
        plaintext = plainbytes.decode('utf-8')
        return plaintext

    def get_cookie_from_chrome(self, host='www.cde.org.cn'):
        local_state = os.environ['LOCALAPPDATA'] + r'\Google\Chrome\User Data\Local State'
        cookie_path = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Default\Cookies"
        
        sql = "select host_key,name,encrypted_value from cookies where host_key='%s'" % host

        with sqlite3.connect(cookie_path) as conn:
            cu = conn.cursor()
            res = cu.execute(sql).fetchall()
            cu.close()
            self.cookies = {}
            key = self.pull_the_key(self.get_string(local_state))
            for host_key, name, encrypted_value in res:
                if encrypted_value[0:3] == b'v10':
                    self.cookies[name] = self.decrypt_string(key, encrypted_value)
                else:
                    self.cookies[name] = CryptUnprotectData(encrypted_value)[1].decode()

            print("===cookies===:{}".format(self.cookies))
            # return cookies
    
    @func_timeout.func_set_timeout(8)
    def __ask_choice(self,message="是否启动Chrome以刷新Cookies?"):
        return input('{}(Y/n):'.format(message))

    def __init__(self):
        self.proxies = {}  # 初始化不开启代理
        self.proxies_url = ""  # 选用代理的ip:port
        self.proxies_retry = 1 # 代理剩余重试次数
        try:
            is_get_cookie = self.__ask_choice()
        except func_timeout.exceptions.FunctionTimedOut:
            print('\n选择超时，将启动Chrome更新Cookies...')
            is_get_cookie = "Y"
        if not is_get_cookie.upper() == 'N':
            chromePath = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            url = 'http://www.cde.org.cn/transparent.do?method=yzxpjSpxlList&taskType=xb'
            webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chromePath))
            browser = webbrowser.get('chrome')
            browser.open(url)
            print("等待10s使浏览器打开和加载页面，以便抓取Cookies...")
            time.sleep(10)
        
        self.header = {
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
        self.get_cookie_from_chrome(host="www.cde.org.cn")
        self.debug_proxies = {}
        # self.debug_proxies = {"http":"http://localhost:11111", 'https':"https://localhost:11111"}
    
    def set_proxy(self):
        self.proxies_url = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
        self.proxies = {"http": "http://{}".format(self.proxies_url)}

    def requests_post(self, url, data={}, headers={}, cookies={}, proxies={}, timeout=5, **extra):
        try:
            response = requests.post(url, data=data, headers=headers, cookies=cookies, proxies=self.proxies, timeout=timeout, **extra)
        except Exception as e:
            print("Error occurred: {}".format(e))
        if 'response' not in locals() or response.status_code != 200:
            print('请求失败，重试中...')
            while True:
                self.proxies_retry = self.proxies_retry - 1
                if self.proxies_retry <= 0:  # 判断现有代理是否已经超出重试次数
                    if self.proxies_url:  # 删除无效代理
                        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(self.proxies_url))
                    # self.proxies_url = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
                    # self.proxies = {"http": "http://{}".format(self.proxies_url)}
                    self.set_proxy()
                    print("更新代理:{}".format(self.proxies))
                    self.proxies_retry = 5 # 重置剩余重试次数
                try:
                    response = requests.post(url, data=data, headers=headers, cookies=cookies, proxies=self.proxies, timeout=timeout, **extra)
                except Exception as e:
                    print("Error occurred: {}".format(e))
                if 'response' in locals() and response.status_code == 200:
                    print("请求成功！")
                    break
                print("请求失败，再次重试...")
        return response
        

    def requests_get(self, url, params={}, headers={}, cookies={}, proxies={}, timeout=5, **extra):
        try:
            response = requests.get(url, params=params, headers=headers, cookies=cookies, proxies=self.proxies, timeout=timeout, **extra)
        except Exception as e:
            print("Error occurred: {}".format(e))
        if 'response' not in locals() or response.status_code != 200:
            print('请求失败，重试中...')
            while True:
                self.proxies_retry = self.proxies_retry - 1
                if self.proxies_retry <= 0:  # 判断现有代理是否已经超出重试次数
                    if self.proxies_url:  # 删除无效代理
                        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(self.proxies_url))
                    # self.proxies_url = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
                    # self.proxies = {"http": "http://{}".format(self.proxies_url)}
                    self.set_proxy()
                    print("更新代理:{}".format(self.proxies))
                    self.proxies_retry = 5 # 重置剩余重试次数
                try:
                    response = requests.get(url, params=params, headers=headers, cookies=self.cookies, proxies=self.proxies, timeout=timeout, **extra)
                except Exception as e:
                    print("Error occurred: {}".format(e))
                if 'response' in locals() and response.status_code == 200:
                    print("请求成功！")
                    break
                print("请求失败，再次重试...")
        return response

    def __check_lamp(self, td_lamp):
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

    def get_yizhixing_data(self, task="xb"):
        """
            一致性数据
        """
        taskType = "xb" if task == "xb" else "fb"
        task = "新报" if taskType == "xb" else "补充"
        print("开始抓取一致性数据({})...".format(taskType))
        datalist = []
        url = 'http://www.cde.org.cn/transparent.do?method=yzxpjSpxlList'
        params = {
            "taskType": taskType,
            "acceptid": "",
            "currentPageNumber": "1",
            "pageMaxNumber": "80",
            "totalPageCount": "42",
            "pageroffset": "",
            "pageMaxNum": "80",
            "pagenum": "1"
        }
        response = requests.post(url,data=params,headers=self.header,cookies=self.cookies, proxies=self.debug_proxies)
        html = response.text
        if len(html) < 30000:
            print('一致性{}数据爬取失败，请求返回异常'.format(task))
            return []
        soup = BeautifulSoup(html)
        page_count = int(soup.find("td", id="pageNumber").font.next_sibling.next_sibling.string)
        print('共发现{}页数据，开始逐页进行获取'.format(page_count))
        for pagenum in range(1, (page_count+1)):
            print('开始获取第{}/{}页数据'.format(pagenum, page_count))
            wait_time = random.randint(3,8)
            print("等待{}s".format(wait_time))
            time.sleep(wait_time)
            params = {
                "taskType": taskType,
                "acceptid": "",
                "currentPageNumber": str(pagenum),
                "pageMaxNumber": "80",
                "totalPageCount": str(page_count),
                "pageroffset": str(len(datalist)),
                "pageMaxNum": "80",
                "pagenum": str(pagenum)
            }
            print("======param=====:{}".format(params))
            response = requests.post(url,data=params,headers=self.header,cookies=self.cookies, proxies=self.debug_proxies)
            html = response.text
            # print(html)
            soup = BeautifulSoup(html)
            temp_data_count = len(soup.find_all('tr', {"class": "newsindex"}))
            if temp_data_count == 0:
                print(html)
                if input("一致性数据爬取失败，是否重试？（Y/n)") == "Y":
                   continue
                else:
                    print('一致性数据抓取中断')
                    tmp = {}
                    for id, ele in enumerate(header):
                        tmp[header[id]] = "err"
                    datalist.append(tmp)
                    break

            print('本页面共发现{}条数据'.format(temp_data_count))
            try:
                for idx, tr in enumerate(soup.find_all('tr', {"class": "newsindex"})):
                    tds = tr.find_all('td')
                    datalist.append({
                        '序号': tds[0].string.strip(),
                        '受理号': tds[1].string.strip(),
                        '药品名称': tds[2].string.strip(),
                        '进入中心时间': tds[3].string.strip(),
                        '统计': self.__check_lamp(tds[4]),
                        '药理毒理': self.__check_lamp(tds[5]),
                        '临床': self.__check_lamp(tds[6]),
                        '药学': self.__check_lamp(tds[7]),
                        '备注': tds[8].contents[0].replace('\n', '').replace('\r', '').replace('\t', '').strip(),
                    })
            except Exception as e:
                print(e)
                _ = input('页面{}分析失败'.format(pagenum))
        print('一致性评价{}数据爬取完毕，共获得数据{}行'.format(task, len(datalist)))
        return datalist
    
    def __check_data_volume(self, datalist, dateStr="承办日期"):
        """判断抓取的数据是否已经满足数量要求

            满足800条 或过去两个月
            此处设定同时满足900条和70天

        """
        date_str = datalist[-1][dateStr]
        interval = datetime.datetime.today() - datetime.datetime.strptime(date_str,"%Y-%m-%d")
        return len(datalist) >= 900 and interval.days > 70

    def get_songda(self):
        """送达数据 
        """
        print("开始抓取送达数据...")
        datalist = []
        header = ['序号', '受理号', '送达时间']
        url = "http://www.cde.org.cn/postInfo.do"
        params = {
            "method": "getList",
            "acceptid": "",
            "currentPageNumber": "1",
            "pageMaxNumber": "80",
            "totalPageCount": "1800",
            "pageroffset": "",
            "pageMaxNum": "80",
            "pagenum": "1"
        }
        print("======param=====:{}".format(params))
        response = requests.post(url,data=params,headers=self.header,cookies=self.cookies, proxies=self.debug_proxies)
        html = response.text
        soup = BeautifulSoup(html)
        if soup.title.string == "":
            print('送达数据请求失败，请检查Cookies')
            return []
        page_count = int(soup.find("td", id="pageNumber").font.next_sibling.next_sibling.string)
        print('共发现{}页数据，开始逐页进行获取'.format(page_count))
        # for pagenum in range(1, 11):
        for pagenum in range(1, (page_count+1)):
            print('开始获取第{}/{}页数据'.format(pagenum, page_count))
            wait_time = random.randint(3,8)
            print("等待{}s".format(wait_time))
            time.sleep(wait_time)
            params = {
                "method": "getList",
                "acceptid": "",
                "currentPageNumber": str(pagenum),
                "pageMaxNumber": "80",
                "totalPageCount": str(page_count),
                "pageroffset": str(len(datalist)),
                "pageMaxNum": "80",
                "pagenum": str(pagenum)
            }
            print("======param=====:{}".format(params))
            response = requests.post(url,data=params,headers=self.header,cookies=self.cookies, proxies=self.debug_proxies)
            html = response.text
            # print(html)
            soup = BeautifulSoup(html)
            data = [] # 存储本页面的数据
            if soup.find("tbody") == None:
                print(html)
                print(response.status_code)
                if input("送达数据爬取失败，是否重试？（Y/n)") == "Y":
                   continue
                else:
                    print('送达数据抓取中断')
                    tmp = {}
                    for id, ele in enumerate(header):
                        tmp[header[id]] = "err"
                    datalist.append(tmp)
                    break
            for line in soup.find("tbody").children: # 选择表格tbody部分
                if not line.string == None:     # 清理空行
                    continue
                tmp = {}
                for id,ele in enumerate(line.find_all('td')):
                    tmp[header[id]] = ele.string.strip()
                data.append(tmp)
            print('本页面共获得{}条数据'.format(len(data)))
            datalist = datalist + data
            if self.__check_data_volume(datalist, dateStr="送达时间"):
                break   # 如果数据量已经满足要求就终止循环
        print('送达数据爬取完毕，共获得数据{}行'.format(len(datalist)))
        return datalist

    def get_shoulimulu(self):
        print("开始抓取受理目录数据...")
        datalist = []
        header = ['受理号', '药品名称', '药品类型', '申请类型', '注册分类', '企业名称', '承办日期']
        url = "http://www.cde.org.cn/transparent.do?method=list"
        params = {
            "checktype": "1",
            "pagetotal": "2000", # 总记录数
            "statenow": "0",
            "year": "2020",  # 年份
            "drugtype": "hy",  # 药品类型：化药
            "applytype": "bcsq",  # 申请类型：补充申请
            "acceptid": "",  # 受理号
            "drugname": "",  # 药品名称
            "company": "",  # 企业名称
            "currentPageNumber": "1",  # 当前页码
            "pageMaxNumber": "80", # 每页条数
            "totalPageCount": "100", # 总页数
            "pageroffset": "",  # 前序页面累积数据量
            "pageMaxNum": "80",  # 每页条数
            "pagenum": "1"  # 当前页码

        }
        response = requests.post(url,data=params,headers=self.header,cookies=self.cookies,proxies=self.debug_proxies)
        html = response.text
        soup = BeautifulSoup(html)
        if soup.title.string.strip() == "":
            print('受理目录数据请求失败，请检查Cookies')
            return []
        page_count = int(soup.find("td", id="pageNumber").font.next_sibling.next_sibling.string)
        record_count = int(soup.find('font',color="#FF0000").string)
        for pagenum in range(1,(page_count+1)):
            print('开始获取第{}/{}页数据'.format(pagenum, page_count))
            wait_time = random.randint(5,10) 
            print("等待{}s".format(wait_time))
            time.sleep(wait_time)
            params = {
                "checktype": "1",
                "pagetotal": str(record_count), # 总记录数
                "statenow": "0",
                "year": "2020",
                "drugtype": "hy",  # 药品类型：化药
                "applytype": "bcsq",  # 申请类型：补充申请
                "acceptid": "",  # 受理号
                "drugname": "",  # 药品名称
                "company": "",  # 企业名称
                "currentPageNumber": str(pagenum),  # 当前页码
                "pageMaxNumber": "80",  # 每页条数
                "totalPageCount": str(page_count), # 总页数
                "pageroffset": str(len(datalist)),  # 前序页面累积数据量
                "pageMaxNum": "80",  # 每页条数
                "pagenum": str(pagenum)  # 当前页码
            }
            print("======param=====:{}".format(params))
            response = requests.post(url,data=params,headers=self.header,cookies=self.cookies,proxies=self.debug_proxies)
            html = response.text
            soup = BeautifulSoup(html)
            # print(html)
            data = [] # 存储本页面的数据
            if soup.find("tbody") == None:
                print(html)
                print(response.status_code)
                if input("err") == "retry":
                   continue
                else:
                    print('送达数据抓取中断')
                    tmp = {}
                    for id, ele in enumerate(header):
                        tmp[header[id]] = "err"
                    datalist.append(tmp)
                    break
            table_field = soup.find("td", {"class": "newsindex"}).parent.parent
            for line in table_field.thead.next_siblings:
                if not line.string == None:     # 清理空行
                    continue
                tmp = {}
                for id, ele in enumerate(line.find_all('td')):
                    tmp[header[id]] = ele.string.strip()
                data.append(tmp)
            print('本页面共获得{}条数据'.format(len(data)))
            datalist = datalist + data
            if self.__check_data_volume(datalist, dateStr="承办日期"):
                break   # 如果数据量已经满足要求就终止循环
        print('受理目录爬取完毕，共获得数据{}行'.format(len(datalist)))
        return datalist
    
    def get_yaopinmulu(self, task="新标准"):
        self.set_proxy()
        print("开始抓取药品目录-{}数据...".format(task))
        taskType = "按化学药品新注册分类批准的仿制药" if task == "新标准" else "通过质量和疗效一致性评价的药品"
        datalist = []
        header = ['批准文号/注册证号','药品名称', '剂型','规格','参比制剂','批准日期','上市许可持有人']
        url = "http://202.96.26.102/index/lists"
        pagenum = 1
        while True:  # 新标准页面的页码是用js加载的，所以直接套死循环，抓不到数据后结束
            print('开始获取第{}页数据'.format(pagenum))
            wait_time = random.randint(5,10)  if not self.proxies_url else 0
            print("等待{}s".format(wait_time))
            time.sleep(wait_time)
            params = {
                "scpzrq_start": " 1990-11-01",
                "scpzrq_end": "2025-12-01",
                # "sllb": "按化学药品新注册分类批准的仿制药",
                "sllb": taskType,
                "page": str(pagenum)
            }
            response = self.requests_get(url, params=params, headers=self.header)
            html = response.text
            soup = BeautifulSoup(html)
            if soup.find("div", {"class": "noData"}):  # 判断是否已抓取完毕，页面无数据后结束
                print("药品目录-{}数据已全部抓取完成，共{}页".format(task, pagenum-1))
                break
            # 页面存在数据，开始进行分析
            data = []  # 存储本页数据
            table_field = soup.find("table", {"class":"drug-lists"})
            for line in table_field.tbody.children:
                if not line.string == None:
                    continue
                tmp = {}
                for id, ele in enumerate(line.find_all("td")):
                    ele_content = ele.string.strip() if ele.string else ""
                    tmp[header[id]] = ele_content
                data.append(tmp)
            print("本页面共获得{}条数据".format(len(data)))
            datalist = datalist + data
            # 为避免空页面限制失效，设置最大循环200页
            if pagenum >= 200:
                break
            pagenum = pagenum + 1
        print('药品目录-{}爬取完毕，共获得数据{}行'.format(task, len(datalist)))
        return datalist


import json
def dump_data_to_file(data):
    with open('data.dump', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    spider = Spider()
    # spider.get_xinbiaozhun()
    # data = spider.get_yaopinmulu()
    # dump_data_to_file(data)


    
    # data = spider.get_shoulimulu()
    # print(data)
    # dump_data_to_file(data)

    # data = spider.get_songda()
    # data = spider.get_yizhixing_data()
    # print(data)
    # print(data)
    # json.dump(data, 'data.dump')



