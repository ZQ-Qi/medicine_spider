#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ExcelModule.py
@Time    :   2020/07/05 23:32:33
@Desc    :   存储表格到Excel
'''

import xlwt
import time

class ExcelModule(object):
    def __init__(self, filename="基础数据.xls"):
        """创建Excel文件对象
        """
        self.filename = filename
        self.workbook = xlwt.Workbook(encoding='utf-8')

    def save_file(self):
        """保存Excel到文件"""
        self.workbook.save(self.filename)

    def write_yizhixing(self, datalist, task="新报"):
        """保存一致性表到Excel工作表。一致性数据包含【新报】和【补充】两类，需指定到task变量，未指定则默认为【新报】
        """
        header = ['序号','受理号','药品名称','进入中心时间', '统计','药理毒理','临床', '药学','备注']
        # 创建工作表
        sheet = self.workbook.add_sheet("{}一致性评价{}".format(task, time.strftime("%Y%m%d",time.localtime())))
        # 表格第一行
        sheet.write(0,0,"{}一致性评价任务{}".format(task, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())))
        # 表格第二行
        sheet.write(1,0,"说明，【进入中心时间】~【药学】阶段，数字1表示本专业未启动，数字2表示本专业正在审评")
        # 表格第三行 标题
        for i, head in enumerate(header):
            sheet.write(2,i,head)
        for i,line in enumerate(datalist):
            for j,head in enumerate(header):
                sheet.write((3+i),j,line[head])
        print('工作表【{}一致性评价任务{}】写入完成'.format(task, time.strftime("%Y%m%d",time.localtime())))
    
    def write_songda(self, datalist):
        """保存送达数据到工作表
        """
        header = ['序号', '受理号', '送达时间']
        # 创建工作表
        sheet = self.workbook.add_sheet("送达信息{}".format(time.strftime("%Y%m%d",time.localtime())))
        # 表格第一行
        sheet.write(0,0,"送达信息{}".format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())))
        # 表格第二行 标题
        for i, head in enumerate(header):
            sheet.write(1,i,head)
        for i,line in enumerate(datalist):
            for j,head in enumerate(header):
                sheet.write((2+i),j,line[head])
        print('工作表【送达时间{}】写入完成'.format(time.strftime("%Y%m%d",time.localtime())))
    
    def write_shoulimulu(self, datalist):
        """保存受理目录到工作表
        """
        header = ['受理号', '药品名称', '药品类型', '申请类型', '注册分类', '企业名称', '承办日期']
        # 创建工作表
        sheet = self.workbook.add_sheet("受理目录{}".format(time.strftime("%Y%m%d",time.localtime())))
        # 表格第一行
        sheet.write(0,0,"受理目录{}".format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())))
        # 表格第二行 标题
        for i, head in enumerate(header):
            sheet.write(1,i,head)
        for i,line in enumerate(datalist):
            for j,head in enumerate(header):
                sheet.write((2+i),j,line[head])
        print('工作表【受理目录{}】写入完成'.format(time.strftime("%Y%m%d",time.localtime())))

    def write_yaopinmulu(self, datalist, task="新标准"):
        """保存药品目录到工作表。药品目录分为【新标准】和【已通过】
        """
        header = ['批准文号/注册证号','药品名称', '剂型','规格','参比制剂','批准日期','上市许可持有人']
        # 创建工作表
        sheet = self.workbook.add_sheet("{}{}".format(task, time.strftime("%Y%m%d",time.localtime())))
        # 表格第一行
        sheet.write(0,0,"药品目录{}{}".format(task, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())))
        # 表格第二行 标题
        for i, head in enumerate(header):
            sheet.write(1,i,head)
        for i,line in enumerate(datalist):
            for j,head in enumerate(header):
                sheet.write((2+i),j,line[head])
        print('工作表【{}】写入完成'.format(task, time.strftime("%Y%m%d",time.localtime())))



if __name__ == '__main__':
    """测试
    """
    excel = ExcelModule('test.xls')
    data = []
    header = ['序号','受理号','药品名称','进入中心时间', '统计','药理毒理','临床', '药学','备注']
    for i in range(10):
        tmp = [x for x in range(i,i+9)]
        data.append(dict(zip(header,tmp)))
    header = ['序号', '受理号', '送达时间']
    excel.write_yizhixing(data)

    data = []
    for i in range(10):
        tmp = [x for x in range(i,i+3)]
        data.append(dict(zip(header, tmp)))
    excel.write_songda(data)
    
    excel.save_file()
    

    
