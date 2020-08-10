#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2020/07/05 23:53:29
@Author  :   QI ZHIQIANG 
@Version :   1.0
@Contact :   153089761@qq.com
@License :   (C)Copyright
@Desc    :   None
'''

import Spider
import ExcelModule
import subprocess
from multiprocessing import Process
import os
import time    

if __name__ == '__main__':
    print("启动IP代理池...")
    p_schedule = Process(target=subprocess.call, args=(['python', './ip_pool/proxyPool.py', 'schedule'],))
    p_schedule.start()
    time.sleep(2)
    p_server = Process(target=subprocess.call, args=(['python', './ip_pool/proxyPool.py', 'server'],))
    p_server.start()
    time.sleep(2)

    spider = Spider.Spider()
    excel = ExcelModule.ExcelModule()
    
    # data = spider.get_yizhixing_data()
    # excel.write_yizhixing(data)
    
    # data = spider.get_yizhixing_data(task='fb')
    # excel.write_yizhixing(data, task="补充")

    # data = spider.get_songda()
    # excel.write_songda(data)

    # data = spider.get_shoulimulu()
    # excel.write_shoulimulu(data)

    data = spider.get_yaopinmulu(task="新标准")
    excel.write_yaopinmulu(data, task="新标准")

    data = spider.get_yaopinmulu(task="已通过")
    excel.write_yaopinmulu(data, task="已通过")
    
    
    excel.save_file()

    print('程序执行完毕，结束代理池')
    p_schedule.terminate()
    p_server.terminate()
    p_schedule.join()
    p_server.join()


