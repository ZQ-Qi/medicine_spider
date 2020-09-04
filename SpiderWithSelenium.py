#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   SpiderWithSelenium.py
@Time    :   
@Desc    :   使用Selenium模拟浏览器抓取一致性、送达、受理目录数据
'''

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time
import random
import datetime

import ExcelModule


class SpiderWithSelenium(object):
    def __init__(self, proxy=""):
        """初始化，创建浏览器对象，并设置初始参数
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--proxy-server={}'.format(proxy))
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
              Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
              })
            """
        })
    
    def close(self):
        """控制浏览器退出"""
        print("进程结束，退出浏览器")
        self.driver.quit()
    
    def __checkLamp(self, td_lamp):
        """根据网页表格指示灯的状态判断进度指示"""
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
            
    def __waiting(self):
        """为避免过早触发反扒机制，在每次访问网页后设定一个随机等待时间"""
        wait_time = random.randint(3,8)
        print("等待{}s".format(wait_time))
        time.sleep(wait_time)

    def getYizhixingData(self, task="xb"):
        """获取一致性数据，一致性数据分为【新报】(task="xb")和【补充】(task="fb")"""
        taskType = "xb" if task == "xb" else "fb"
        task = "新报" if taskType == "xb" else "补充"
        print("开始抓取一致性数据({})...".format(taskType))
        datalist = []
        base_url = ("http://www.cde.org.cn/transparent.do?"
        "method=yzxpjSpxlList&taskType={}"
        "&currentPageNumber={}"
        "&pageMaxNumber={}"
        "&totalPageCount={}"
        "&pageroffset={}"
        "&pageMaxNum={}"
        "&pagenum={}")
        url = base_url.format(taskType, 1, 80, 42, "", 80, 1)
        self.driver.get(url)
        self.__waiting()
        html = self.driver.page_source
        soup = BeautifulSoup(html)
        page_count = int(soup.find("td", id="pageNumber").font.next_sibling.next_sibling.string)
        print('共发现{}页数据，开始逐页进行获取'.format(page_count))
        for pagenum in range(1, (page_count+1)):
            # wait_time = random.randint(3,8)
            # print("等待{}s".format(wait_time))
            # time.sleep(wait_time)

            print('开始获取第{}/{}页数据'.format(pagenum, page_count))
            url = base_url.format(taskType, pagenum, 80, page_count, len(datalist), 80, pagenum)
            self.driver.get(url)
            self.__waiting()
            html = self.driver.page_source
            soup = BeautifulSoup(html)
            temp_data_count = len(soup.find_all('tr', {"class": "newsindex"}))
            print('本页面共发现{}条数据'.format(temp_data_count))
            try:
                for idx, tr in enumerate(soup.find_all('tr', {"class": "newsindex"})):
                    tds = tr.find_all('td')
                    datalist.append({
                        '序号': tds[0].string.strip(),
                        '受理号': tds[1].string.strip(),
                        '药品名称': tds[2].string.strip(),
                        '进入中心时间': tds[3].string.strip(),
                        '统计': self.__checkLamp(tds[4]),
                        '药理毒理': self.__checkLamp(tds[5]),
                        '临床': self.__checkLamp(tds[6]),
                        '药学': self.__checkLamp(tds[7]),
                        '备注': tds[8].contents[0].replace('\n', '').replace('\r', '').replace('\t', '').strip(),
                    })
            except Exception as e:
                print(e)
                _ = input('页面{}分析失败'.format(pagenum))
        print('一致性评价{}数据爬取完毕，共获得数据{}行'.format(task, len(datalist)))
        return datalist
    def __checkDataVolume(self, datalist, dateStr="承办日期"):
        """判断抓取的数据是否已经满足数量要求

            满足800条 或过去两个月
            此处设定同时满足900条和70天

        """
        date_str = datalist[-1][dateStr]
        interval = datetime.datetime.today() - datetime.datetime.strptime(date_str,"%Y-%m-%d")
        return len(datalist) >= 900 and interval.days > 70

    def getSongdaData(self):
        """获取送达数据
        """
        print("开始抓取送达数据...")
        datalist = []
        header = ['序号', '受理号', '送达时间']
        base_url = ("http://www.cde.org.cn/postInfo.do?"
        "method=getList"
        "&currentPageNumber={}"
        "&pageMaxNumber={}"
        "&totalPageCount={}"
        "&pageroffset={}"
        "&pageMaxNum={}"
        "&pagenum={}")
        url = base_url.format(1, 80, 1800, "", 80, 1)
        self.driver.get(url)
        self.__waiting()
        html = self.driver.page_source
        soup = BeautifulSoup(html)
        page_count = int(soup.find("td", id="pageNumber").font.next_sibling.next_sibling.string)
        print('共发现{}页送达数据，开始逐页进行获取'.format(page_count))
        for pagenum in range(1, (page_count+1)):
            # wait_time = random.randint(3,8)
            # print("等待{}s".format(wait_time))
            # time.sleep(wait_time)
            print('开始获取第{}/{}页数据'.format(pagenum, page_count))
            url = base_url.format(pagenum, 80, page_count, len(datalist), 80, pagenum)
            self.driver.get(url)
            self.__waiting()
            html = self.driver.page_source
            soup = BeautifulSoup(html)
            data = [] # 存储本页面的数据
            for line in soup.find_all("tbody")[5].children: # 选择表格tbody部分
                if not line.string == None:     # 清理空行
                    continue
                tmp = {}
                for id,ele in enumerate(line.find_all('td')):
                    # print(ele.string)
                    tmp[header[id]] = ele.string.strip()
                data.append(tmp)
            print('本页面共获得{}条数据'.format(len(data)))
            datalist = datalist + data
            if self.__checkDataVolume(datalist, dateStr="送达时间"):
                break   # 如果数据量已经满足要求就终止循环
        print('送达数据爬取完毕，共获得数据{}行'.format(len(datalist)))
        return datalist

    def getShoulimuluData(self):
        """获取受理目录数据
        """
        print("开始抓取受理目录数据...")
        datalist = []
        header = ['受理号', '药品名称', '药品类型', '申请类型', '注册分类', '企业名称', '承办日期']
        base_url = ("http://www.cde.org.cn/transparent.do?"
        "method=list"
        "&checktype=1"
        "&pagetotal={}"
        "&statenow=0" # 0-受理品种目录浏览 1-在审品种目录浏览
        "&year=2020" # 年份
        "&drugtype=hy"  # 药品类型：化药
        "&applytype=bcsq"  # 申请类型：补充申请
        "&currentPageNumber={}"  # 当前页码
        "&pageMaxNumber=80"
        "&totalPageCount={}"
        "&pageroffset={}"
        "&pageMaxNum=80"
        "&pagenum={}")
        url = base_url.format(0, 1, 0, "", 1)
        self.driver.get(url)
        self.__waiting()
        html = self.driver.page_source
        soup = BeautifulSoup(html)
        page_count = int(soup.find("td", id="pageNumber").font.next_sibling.next_sibling.string)
        record_count = int(soup.find('font',color="#FF0000").string)
        for pagenum in range(1,(page_count+1)):
            # wait_time = random.randint(5,10) 
            # print("等待{}s".format(wait_time))
            # time.sleep(wait_time)
            print('开始获取第{}/{}页受理目录数据'.format(pagenum, page_count))
            url = base_url.format(record_count, pagenum, page_count, len(datalist), pagenum)
            self.driver.get(url)
            self.__waiting()
            html = self.driver.page_source
            soup = BeautifulSoup(html)
            data = [] # 存储本页面的数据
            
            for line in soup.find_all("tbody")[6].children:
                if not line.string == None:     # 清理空行
                    continue
                tmp = {}
                for id,ele in enumerate(line.find_all('td')):
                    # print(ele.string)
                    tmp[header[id]] = ele.string.strip()
                data.append(tmp)
            print('本页面共获得{}条数据'.format(len(data)))
            datalist = datalist + data
            if self.__checkDataVolume(datalist, dateStr="承办日期"):
                break   # 如果数据量已经满足要求就终止循环
        print('受理目录爬取完毕，共获得数据{}行'.format(len(datalist)))
        return datalist

if __name__ == "__main__":
    sws = SpiderWithSelenium()
    excel = ExcelModule.ExcelModule()

    # data = sws.getYizhixingData()
    # excel.write_yizhixing(data)

    # data = sws.getSongdaData()
    # excel.write_songda(data)

    data = sws.getShoulimuluData()
    excel.write_shoulimulu(data)

    excel.save_file()

    sws.close()