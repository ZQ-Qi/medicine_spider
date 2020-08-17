#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
import random
from bs4 import BeautifulSoup
import requests

class ExitException(Exception):
    "用于要求上层方法终止当前任务"
    def __init__(self, leng="Too much retried."):
        self.leng = leng
    def __str__(self):
        print(self.leng)


class SpiderWithRequests(object):
    "使用Requests请求构建爬虫"
    def set_proxy(self):
        "设置代理"
        self.proxies_url = requests.get("http://127.0.0.1:5010/get/").json().get("proxy")
        self.proxies = {"http": "http://{}".format(self.proxies_url)}

    def __init__(self, isproxy=False, proxy_on_startup=True):
        "初始化，根据是否代理，何时代理设置重试次数"
        self.proxies = {}  # 初始化不开启代理
        self.proxies_url = ""  # 选用代理的ip:port
        # 如果启用代理且不立即使用，则本地ip爬取直到第一次失败
        # 如果启用代理且立即启用，则直接设置代理
        # 如果不启用代理，则本地重试失败（长间隔）20次后，终止爬取（不推荐）
        self.isproxy = isproxy
        if not self.isproxy:
            self.proxies_retry = 20
        elif proxy_on_startup:
            self.set_proxy()
            self.proxies_retry = 5
        else:
            self.proxies_retry = 1
        
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


    def requests_get(self, url, params={}, headers={}, cookies={}, proxies={}, timeout=5, **extra):
        "构建GET请求，并处理各类异常"
        try:
            response = requests.get(url, params=params, headers=headers, cookies=cookies, proxies=self.proxies, timeout=timeout, **extra)
        except Exception as e:
            print("Error occurred: {}".format(e))
        if 'response' not in locals() or response.status_code != 200:
            # 判断是否启用代理，若未启用则定时循环重试，直到max_retry
            if not self.isproxy:  # 未启用代理
                print("触发反爬虫，进行5分钟等待")
                time.sleep(300)
                while True:
                    self.proxies_retry = self.proxies_retry - 1
                    if self.proxies_retry <= 0:  # 判断现有代理是否已经超出重试次数
                        raise ExitException("本地重试超出最大重试次数，终止爬取")
                    try:
                        response = requests.get(url, params=params, headers=headers, cookies=cookies, proxies=self.proxies, timeout=timeout, **extra)
                    except Exception as e:
                        print("Error occurred: {}".format(e))
                    if 'response' in locals() and response.status_code == 200:
                        print("请求成功！")
                        break
                    print("请求失败，再次重试...")
            print('请求失败，重试中...')
            while True:
                self.proxies_retry = self.proxies_retry - 1
                if self.proxies_retry <= 0:  # 判断现有代理是否已经超出重试次数
                    if self.proxies_url:  # 删除无效代理
                        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(self.proxies_url))
                    self.set_proxy()
                    print("更新代理:{}".format(self.proxies))
                    self.proxies_retry = 5 # 重置剩余重试次数
                try:
                    response = requests.get(url, params=params, headers=headers, cookies=cookies, proxies=self.proxies, timeout=timeout, **extra)
                except Exception as e:
                    print("Error occurred: {}".format(e))
                if 'response' in locals() and response.status_code == 200:
                    print("请求成功！")
                    break
                print("请求失败，再次重试...")
        return response
    
    def getYaopinmuluData(self, task="新标准"):
        "抓取药品目录数据"
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
            try:
                response = self.requests_get(url, params=params, headers=self.header)
            except ExitException as e:
                print(e)
                return datalist
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

if __name__ == '__main__':
    pass