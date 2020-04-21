import os
import re
import time
import threading
from multiprocessing import Pool, cpu_count

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agents': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',

}

Url = 'https://www.meitucha.com'
lock = threading.Lock()
Dir_path = r"E:/photo"

def serch(name):         #查询当前名字下的所有套图，返回套图的链接与标题
    url = Url + '/search?keyword='+ name    #拼接url
    html = requests.get(url,headers=HEADERS,timeout=80).text
    root_soup_html = BeautifulSoup(html,'lxml')
    url_doc = root_soup_html.find('ul', class_ ='img').find_all('li')
    root_urls = []       #存储页面查找到的所有套图的链接
    for url in url_doc:
        root_url = url.a['href']
        root_url = Url + root_url
        print(root_url)
        root_urls.append(root_url)

    titles = root_soup_html.find('ul',class_ = 'img').find_all('p',class_='biaoti')

    for title in titles:
        title = title.find('a').string
        #print(title)
    return root_urls,titles

def get_img(root_url):     # 返回当前套图下的所有图片
    soup_html = BeautifulSoup(requests.get(root_url,headers = HEADERS,timeout=200).text,'lxml')
    doc = soup_html.find('div',class_="pg").find_all('a')[-1]
        
    max_count = re.search('page=(.*?)"',str(doc)).group(1)
    print(max_count,'\n')
    urls = [root_url + str(i) for i in range(1,int(max_count)+1)]
    print(urls)
    img_urls = []

    with lock:
        for url in urls:      #爬取每一个网页
            try:
                img_doc = BeautifulSoup(requests.get(url,headers = HEADERS,timeout=150).text,'lxml')
                imgs = img_doc.find('div',class_='content').find_all('img')
                print(imgs)
                
                for img in imgs:   #爬取每一个网页的照片
                    img_url = img.get('src')
                    print(img_url)
                img_urls.append(img_url)
            except Exception as e:
                print(e)
    time.sleep(1)
    return img_urls
def save_pic(urls,name):
    path = os.path.join(Dir_path,name)
    os.makedirs(path)
    os.chdir(path)
    cnt = 1
    for url in urls:
        try:
            time.sleep(0.10)
            img = requests.get(url, headers =HEADERS,timeout=10)
            img_name = cnt
            cnt +=1
            with open (img_name, 'ab') as f:
                f.write(img.content)
                print(img_name)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    name = "阿朱"
    #name =  input("输入想查询的名字:")                      # 输入想要查询的名字
    root_urls,titles = serch(name)
    pool = Pool(processes=cpu_count())
    cnt = 0
    for root_urls in root_urls:
        img_urls = get_img(root_urls)
        save_pic(img_urls,titles[cnt])
