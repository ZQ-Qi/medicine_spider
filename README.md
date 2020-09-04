# medicine_spider

本程序用于抓取CDE中的特定数据，并存储于Excel表格中。

程序主要由Python3构建，IP代理池部分使用了Github项目[jhao104/proxy_pool](https://github.com/jhao104/proxy_pool)，该项目需要依赖安装Redis数据库

## 安装配置

### Anaconda
本项目基于Python3.8，建议直接安装Python的发行版[Anaconda3](https://www.anaconda.com/products/individual)。

安装过程可以参考网上的教程文章，并更改conda源和pip源至国内节点。

安装完成后，终端执行python能够进入Python交互界面即可。

此外，还需要安装本程序所需的包依赖，见`requirements.txt`（手动整理，可能存在遗漏，若未全部覆盖，可根据程序报错自行安装剩余依赖）

`requirements.txt`调用方法：终端执行下述命令：
```bash
pip install -r requriements.txt 
```
或者，可以安装`req_extend.txt`内的所有包，该依赖列表除本程序需要的依赖外还包含一些Anaconda自带的包，安装方法与调用`requirements.txt`安装依赖的方法类似:
```bash
pip install -r req_extend.txt
```


### Redis
下载：[Redis Windows版本](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FMicrosoftArchive%2Fredis%2Freleases)
下载安装包，安装时勾选添加到PATH，并启用自动运行，（建议）勾选数据库最大内存限制1G~500M
具体可以参考文章：[windows下安装和配置Redis](https://www.jianshu.com/p/e16d23e358c0)

### VSCode(可选)
本程序使用VSCode开发

## 使用
使用VSCode打开文件夹（Open Folder),运行`main.py`即可（注：部分数据的爬取过程需要借助浏览器模拟，相关工作完成后会自动关闭，请勿随意关闭浏览器窗口）

若不借助VSCode等IDE工具，直接在项目根目录下执行`python ./main.py`也可正常运行

## 更新IP代理池脚本
ip_pool通过抓取在线的免费代理节点，收集免费的代理节点并通过切换IP代理的方式避免爬取过程中封禁IP的问题。因为代理池是在线的，部分代理源可能在一段时间后失效导致ip_pool抓取到的可用节点变少甚至失效。对此，可通过更新ip_pool模块来解决问题。

为使输出窗口输出的内容更加简洁，对原`ip_pool`项目的日志级别进行调整，减少ip代理池在python输出窗口的无用输出。

若要更新ip_pool项目，下载[jhao104/proxy_pool](https://github.com/jhao104/proxy_pool)项目代码，并直接覆盖于`.\ip_pool\`文件夹内。

配置IP代理池的数据库端口。编辑`.\ip_pool\setting.py`，修改`DB_CONN`如下（若Redis未采用默认端口安装，更改为对应端口）
```
DB_CONN = 'redis://:@127.0.0.1:6379/0'
```

此外，还需编辑`.\ip_pool\handler\logHandler.py`，更改49行附近的`__init__`方法的代码，将日志级别由`level=DEBUG`到`level=WARNING`如下：
```
def __init__(self, name, level=WARNING, stream=True, file=True):
```

## 故障排查
若程序出现报错，无法正常运行，多是由下述问题引起，可逐一排查尝试解决

1. 检查报错信息，查看是否有包未安装或安装版本不正确
2. 检查网络条件，是否可以正常访问网络
3. 检查Redis服务是否正常运行，是否运行于默认端口(6379)
4. 检查是否已经触发网站的反扒策略
5. 检查网页是否由于改版等导致网页、表格结构变化
6. 检查Chromedriver.exe版本

