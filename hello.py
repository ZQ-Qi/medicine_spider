#！/usr/bin/env python3
# -*- coding: utf-8 -*-

'测试文档'

__author__ = 'Qi'

# import sys

# def test():
#     args = sys.argv
#     if len(args)==1:
#         print('Hello, world!')
#     elif len(args)==2:
#         print('Hello, %s!' % args[1])
#     else:
#         print('Too many arguments!')

# if __name__=='__main__':
#     test()

# def foo(s):
#     n = int(s)
#     if n==0:
#         raise ValueError('invalid value: %s' % s)
#     return 10 / n

# def bar():
#     try:
#         foo('0')
#     except ValueError as e:
#         print('ValueError!')
#         raise

# bar()



# # 子进程要执行的代码
# from multiprocessing import Process
# import os
# import time

# def run_proc(name):
#     print('Run child process %s (%s)...' % (name, os.getpid()))
#     print('child process wait 10s')
#     time.sleep(10)
#     print('child process finished waiting')

# if __name__=='__main__':
#     print('Parent process %s.' % os.getpid())
#     p = Process(target=run_proc, args=('test',))
#     print('Child process will start.')
#     p.start()
#     print('parent process sleep 5s')
#     time.sleep(5)
#     print('parnet process finished sleeping')  
#     p.join()  
#     print('Child process end.')


# 线程池
# from multiprocessing import Pool
# import os, time, random

# def long_time_task(name):
#     print('Run task %s (%s)...' % (name, os.getpid()))
#     start = time.time()
#     time.sleep(random.random() * 10)
#     end = time.time()
#     print('Task %s runs %0.2f seconds.' % (name, (end - start)))

# if __name__=='__main__':
#     print('Parent process %s.' % os.getpid())
#     p = Pool(4)
#     for i in range(10):
#         p.apply_async(long_time_task, args=(i,))
#     print('Waiting for all subprocesses done...')
#     p.close()
#     p.join()
#     print('All subprocesses done.')

# 外部子线程
# import subprocess

# print('$ nslookup www.python.org')
# r = subprocess.call(['nslookup', 'www.python.org'])
# print('Exit code:', r)


# 进程间通信
# from multiprocessing import Process, Queue
# import os, time, random

# # 写数据进程执行的代码:
# def write(q):
#     print('Process to write: %s' % os.getpid())
#     for value in ['A', 'B', 'C']:
#         print('Put %s to queue...' % value)
#         q.put(value)
#         time.sleep(random.random()*3)

# # 读数据进程执行的代码:
# def read(q):
#     print('Process to read: %s' % os.getpid())
#     while True:
#         print('check')
#         value = q.get(True)
#         print('Get %s from queue.' % value)

# if __name__=='__main__':
#     # 父进程创建Queue，并传给各个子进程：
#     q = Queue()
#     pw = Process(target=write, args=(q,))
#     pr = Process(target=read, args=(q,))
#     # 启动子进程pw，写入:
#     pw.start()
#     # 启动子进程pr，读取:
#     pr.start()
#     # 等待pw结束:
#     pw.join()
#     # pr进程里是死循环，无法等待其结束，只能强行终止:
#     pr.terminate()


# from xml.parsers.expat import ParserCreate

# class DefaultSaxHandler(object):
#     def start_element(self, name, attrs):
#         print('sax:start_element: %s, attrs: %s' % (name, str(attrs)))

#     def end_element(self, name):
#         print('sax:end_element: %s' % name)

#     def char_data(self, text):
#         print('sax:char_data: %s' % text)

# xml = r'''<?xml version="1.0"?>
# <ol>
#     <li><a href="/python">Python</a></li>
#     <li><a href="/ruby">Ruby</a></li>
# </ol>
# '''

# handler = DefaultSaxHandler()
# parser = ParserCreate()
# parser.StartElementHandler = handler.start_element
# parser.EndElementHandler = handler.end_element
# parser.CharacterDataHandler = handler.char_data
# parser.Parse(xml)

# from html.parser import HTMLParser
# from html.entities import name2codepoint

# class MyHTMLParser(HTMLParser):

#     def handle_starttag(self, tag, attrs):
#         print('starttag<%s>' % tag)

#     def handle_endtag(self, tag):
#         print('endtag</%s>' % tag)

#     def handle_startendtag(self, tag, attrs):
#         print('startendtag<%s/>' % tag)

#     def handle_data(self, data):
#         print('data:{}'.format(data))

#     def handle_comment(self, data):
#         print('comment<!--', data, '-->')

#     def handle_entityref(self, name):
#         print('entityref:&%s;' % name)

#     def handle_charref(self, name):
#         print('charref: &#%s;' % name)

# parser = MyHTMLParser()
# parser.feed('''<html>
# <head></head>
# <body>
# <!-- test html parser -->
#     <p>Some <a href=\"#\">html</a> HTML&nbsp;tutorial...<br>END</p>
# </body></html>''')


# 图形界面
# from tkinter import *

# class Application(Frame):
#     def __init__(self, master=None):
#         Frame.__init__(self, master)
#         self.pack()
#         self.createWidgets()

#     def createWidgets(self):
#         self.helloLabel = Label(self, text='Hello, world!')
#         self.helloLabel.pack()
#         self.quitButton = Button(self, text='Quit', command=self.quit)
#         self.quitButton.pack()

# app = Application()
# # 设置窗口标题:
# app.master.title('Hello World')
# # 主消息循环:
# app.mainloop()
# 导入tkinter包，为其定义别名tk
# import tkinter as tk
 
# # 定义Application类表示应用/窗口，继承Frame类
# class Application(tk.Frame):
#     # Application构造函数，master为窗口的父控件
#     def __init__(self, master=None):
#         # 初始化Application的Frame部分
#         tk.Frame.__init__(self, master)
#         # 显示窗口，并使用grid布局
#         self.grid()
#         # 创建控件
#         self.createWidgets()
 
#     # 创建控件
#     def createWidgets(self):
#         # 创建一个文字为'Quit'，点击会退出的按钮
#         self.quitButton = tk.Button(self, text='Quit', command=self.quit)
#         # 显示按钮，并使用grid布局
#         self.quitButton.grid()
 
# # 创建一个Application对象app
# app = Application()
# # 设置窗口标题为'First Tkinter'
# app.master.title = 'First Tkinter'
# # 主循环开始
# app.mainloop()


