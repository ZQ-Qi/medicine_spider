from bs4 import BeautifulSoup
import requests

# with open('html.txt', 'r') as f:
#     html = f.read()
#     soup = BeautifulSoup(html)
#     page_count = int(soup.find("td", id="pageNumber").font.next_sibling.next_sibling.string)
#     record_count = int(soup.find('font',color="#FF0000").string)
#     print(record_count)
#     print(page_count)
#     table_field = soup.find("td", {"class": "newsindex"}).parent.parent
#     for line in table_field.thead.next_siblings:
#         if not line.string == None:     # 清理空行
#             continue
#         tmp = {}
#         for id, ele in enumerate(line.find_all('td')):
#             print(ele.string.strip())
        
    
with open('xinbiaozhun1.txt', 'r') as f:
    html = f.read()
    soup = BeautifulSoup(html)
    if soup.find("div", {"class": "noData"}):
        print("新标准数据已全部抓取完成，共{}页".format(1))
        
    table_field = soup.find("table", {"class":"drug-lists"})
    # page_count = soup.find("span", {"class":"total-nums"}).string
    # print(int(page_count))
    for line in table_field.tbody.children:
        if not line.string == None:
            continue
        for id, ele in enumerate(line.find_all("td")):
            ele_content = ele.string.strip() if ele.string else ""
            # if ele.string:
            #     ele_content = ele.string.strip()
            # else:
            #     ele_content = ""
            
            print(ele_content)

        input('------------')


# url = "http://202.96.26.102/index/lists"
# params = {
#     "scpzrq_start": " 1990-11-01",
#     "scpzrq_end": "2025-12-01",
#     "sllb": "按化学药品新注册分类批准的仿制药",
#     "page": "25"
# }
# response = requests.get(url, params=params)
# html = response.text
# with open('xinbiaozhun1.txt', 'w') as f:
#     f.write(html)
# print(html)
# soup = BeautifulSoup(html)