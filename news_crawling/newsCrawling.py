'''
crawling news articles of the different meida.
'''
import pandas as pd
import os
import random
import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
import re
import json
from requests.adapters import HTTPAdapter


PROCESS_GDELT_PATH = "F:\\EventKG\\GDELTEventKG\\BackEnd\\public\\process\\"

VPNPORT = '7890'

PROXIES= {'http':'http://127.0.0.1:' + VPNPORT,'https':'http://127.0.0.1:' + VPNPORT}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.52'
}


def unique_url_about_source_domain(tmp_domian):
    if not os.path.exists("./txt/"):
        os.makedirs("./txt/")
    unique_path = "./txt/unique_url_about_" + tmp_domian + ".txt"
    if os.path.exists(unique_path):
        print(unique_path, "existed!")
        fr = open(unique_path)
        lines = fr.readlines()
        fr.close()
        return set([line.strip() for line in lines])

    tmp_domain_urls = []
    for i in os.listdir(PROCESS_GDELT_PATH):
        tmp = pd.read_csv(PROCESS_GDELT_PATH+i)
        for row in tmp.itertuples():
            source_url_domain = getattr(row, 'SOURCEURL')
            if tmp_domian in source_url_domain.split("//")[-1].split("/")[0]:
                day = getattr(row, 'Day')
                tmp_domain_urls.append(source_url_domain+"+"+str(day))

    tmp_domain_urls_set = set(tmp_domain_urls)
    tmp_domain_urls_list = [el+'\n' for el in tmp_domain_urls_set]
    print("the url number of the {} is:{}".format(tmp_domian, len(tmp_domain_urls_list)))

    f=open(unique_path,"w")
    f.writelines(tmp_domain_urls_list)
    f.close()

    return tmp_domain_urls_set


def regen_tmp_domain_urls_set(tmp_domain):
    unique_path = './txt/unique_url_about_' + tmp_domain +'.txt'
    error_path = './txt/error_url_' + tmp_domain +'.txt'
    
    fr = open(unique_path)
    lines = fr.readlines()
    fr.close()
    
    url_data = {}
    for line in lines:
        url_data[line.strip().split('+')[0]] = line.strip().split('+')[1]

    fr = open(error_path)
    lines = fr.readlines()
    fr.close()
    
    tmp_domain_urls_set = set([line.strip()+"+"+url_data[line.strip()] for line in lines])
    return tmp_domain_urls_set



def generate_random_str(randomlength=16):
    random_str =''
    base_str ='ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length =len(base_str) -1
    for i in range(randomlength):
        random_str +=base_str[random.randint(0, length)]
    return random_str




def craw_articles(tmp_domain_urls_set,tmp_domain, div_article, div_attrs, use_sub=False, h_x='h1', h_in=False, h_attrs={}): # use_sub是否创建子文件夹
    sub_path = "./articles/" + tmp_domain+"/"
    if not os.path.exists(sub_path):
        os.makedirs(sub_path)
    

    error_url = []
    for urli in tmp_domain_urls_set:
        try:
            sess = requests.Session()
            sess.mount('http://', HTTPAdapter(max_retries=10))
            sess.mount('https://', HTTPAdapter(max_retries=10))
            sess.keep_alive = False
            
            day = urli.split("+")[-1]
            url = urli.split("+")[0]
            
            
            if use_sub:
                sub_tmp_domain = urli.split(tmp_domain + "/")[-1].split("/")[0]
                sub_path = "./articles/" + tmp_domain+"/" + sub_tmp_domain+"/"
            if not os.path.exists(sub_path):
                os.makedirs(sub_path)
            
            test_request = requests.get(url, proxies=PROXIES, headers=HEADERS, timeout=10)
            print("state code: ", test_request.status_code)
            
            if test_request.status_code != 200:
                error_url.append(url+'\n')
            
            content = test_request.text
            soup = BeautifulSoup(content, 'html.parser')

            content_div = soup.find(name=div_article, attrs=div_attrs)

            if len(h_attrs) != 0:
                if h_in:
                    new_title = content_div.find_all(h_x, attrs=h_attrs)
                else:
                    new_title = soup.find_all(h_x, attrs=h_attrs)
            else:
                if h_in:
                    new_title = content_div.find_all(h_x)
                else:
                    new_title = soup.find_all(h_x)
            
            print("new_title: ", new_title, "len(new_title): ", len(new_title))

            new_paragraph_list = content_div.find_all("p")
            
            article = []
            title = '_'
            for h in new_title:
                if h.text.strip() == '':
                    print("title list is None")
                    continue
                
                simple_punctuation = '[!"‘’“”#$%&\'()*+,-/:;<=>?@[\\]^_`{|}~，。,]'
                title = re.sub('[\u4e00-\u9fa5]','',h.text)
                title = re.sub(simple_punctuation, '', title)
                print('title:',title)
                title = title.replace('\\n','').replace('Premium','')
                print("==title==process==", title)
                title = title.strip()
                article.append(h.text+'\n')
                
                break

            if title == '_':
                title = day + "+" + generate_random_str()
            else:
                title = day + title
            article.append(day+"\n")
            article.append(url+"\n")
            
            # new_paragraph_list = content_div.find('div',attrs={'class':'article-text ds-container svelte-1efvmlf'})
            # print(new_paragraph_list)

            for p in new_paragraph_list:
                paragraph = p.text
                paragraph = paragraph.encode("gbk", 'ignore').decode("gbk", "ignore")
                paragraph=re.sub('[\u4e00-\u9fa5]', '', paragraph)
                simple_punctuation = '[‘’“”–，。]'
                paragraph = re.sub(simple_punctuation, '', paragraph)
                article.append(paragraph+'\n')

            f=open(sub_path + title + ".txt","w", encoding='utf8')
            f.writelines(article)
            f.close()
        
        except Exception as e:
            print("Exception: ",e)
            print("URL: ",url)
            error_url.append(url+'\n')
    
    f=open("./txt/error_url_" + tmp_domain + ".txt","w") 
    f.writelines(error_url)
    f.close()


def readJson(filepath):
    with open(filepath, 'r') as fp:
        ans = json.load(fp)
    return ans


if __name__ == "__main__":

    # all different media in "../media_statistic/source_url_domain_dict.json"

    # # ============================================================
    # # manually to fix the attributes
    # # ============================================================
    # tmp_domain = 'hotair.com'
    # error_url_txt = "./txt/error_url_" + tmp_domain + ".txt"
    # div_article = 'article'
    # div_attrs = {
    #     # 'class' : re.compile("css-1iqzmgw")
    # }
    # h_x = 'h1'
    # h_in = False
    # h_in = True
    # h_attrs = {
    #     # 'class' : re.compile('css-1bo5zl0')
    # }
    # # ============================================================
    # # ============================================================
    
    # if not os.path.exists(error_url_txt):
    #     tmp_domain_urls_set = unique_url_about_source_domain(tmp_domain)
    #     craw_articles(tmp_domain_urls_set,tmp_domain, div_article=div_article, div_attrs=div_attrs, use_sub=False, h_x=h_x, h_in=h_in, h_attrs=h_attrs)
    # else:
    #     print("existed!")
    #     tmp_domain_urls_set = regen_tmp_domain_urls_set(tmp_domain)
    #     craw_articles(tmp_domain_urls_set,tmp_domain, div_article=div_article, div_attrs=div_attrs, use_sub=False, h_x=h_x, h_in=h_in, h_attrs=h_attrs)

    pass