'''
预处理不同新闻文档
'''

import os
import re
import json
import numpy as np


# 读取文件所有行
def readFile(filepath):
    fr = open(filepath, encoding='utf8',errors='ignore')
    arrayLines = fr.readlines()
    fr.close()
    return arrayLines


# 处理每篇文档
def process_article(filepath, targetdir):
    if not os.path.exists(filepath):
        return
    if not os.path.exists(targetdir):
        os.makedirs(targetdir)

    print(filepath)
    arrayLines = readFile(filepath)

    if len(arrayLines) <= 3:
        return
    
    # 新闻标题
    idx = 0
    title = arrayLines[idx].strip()
    while title == "":
        idx += 1
        title = arrayLines[idx].strip()
    title = " ".join([re.sub('[^A-Za-z0-9]','', re.sub('\W+','', ik)) for ik in title.split(' ')])
    idx +=1
    
    # 新闻发布日期
    timeday = arrayLines[idx].strip()
    while len(timeday) != 8:
        idx +=1
        timeday = arrayLines[idx].strip()
    
    # 新闻链接
    idx +=1
    url = arrayLines[idx].strip()
    while 'http' not in url.lower():
        idx += 1
        url = arrayLines[idx].strip()
    
    # 保存的内容
    article = []
    article.append(title + '\n')
    article.append(timeday + '\n')
    article.append(url + '\n')
    content = []
    # 过滤新闻内容
    idx +=1
    for line in arrayLines[idx:]:
        line = line.strip()
        if len(line) == 0 or len(line.split(' ')) < 15: # 行为空或者单词数少于15个，则忽略该行
            continue
        else:
            # 只保留英文和数字，删除其余字符
            # line = " ".join([re.sub('[^A-Za-z0-9]','', re.sub('\W+','', ik)) for ik in line.split(' ')])
            
            # 只保留英文、数字、英文符号
            line = " ".join([re.sub('[^A-Za-z0-9^$^\'^"^.^,^:^?^!^-]','', ik) for ik in line.split(' ')])
            
            content.append(line + '\n')

    # 保存新闻
    save_title = re.sub(r" +",' ', title)
    save_title = " ".join(save_title.split(" ")[:15])
    f=open(targetdir + save_title + ".txt","w", encoding='utf8',errors='ignore')
    f.writelines(article + list(set(content)))
    f.close()



def process_domain_articles(tmp_domain, use_sub_dir=False, sourcedir='./articles/', topic="RUS_UKR"):

    tmp_domain_root_path =  sourcedir + tmp_domain + '/'
    filter_files = []
    tmp_domain_subdir = os.listdir(tmp_domain_root_path)
    
    if use_sub_dir:
        for subdir in tmp_domain_subdir:
            subdir_dict = {}
            subdir_dict['dir'] = subdir

            # files_in_msn_subdir = os.listdir(tmp_domain_root_path)
            files_in_msn_subdir = os.listdir(tmp_domain_root_path + subdir + '/')
            subdir_dict['new'] = []
            for file in files_in_msn_subdir:
                if 'Whoops' in file or '+' in file or 'Oops' in file or 'Internal Privoxy Error' in file:
                    continue
                else:
                    subdir_dict['new'].append(file)

            filter_files.append(subdir_dict)
    else:
        for subdir in tmp_domain_subdir:
            if 'Whoops' in subdir or '+' in subdir or 'Oops' in subdir or 'Internal Privoxy Error' in subdir \
            or 'The page you are looking for has either moved or expired' in subdir:
                continue
            else:
                filter_files.append(tmp_domain_root_path + subdir)
        

    
    print(filter_files)

    save_tmp_domain = tmp_domain

    for subdir in filter_files:
        sub_path = './' + topic + '/p_articles/' + save_tmp_domain + "/"
        if use_sub_dir:
            for file in subdir['new']:
                # print(save_tmp_domain)
                process_article(tmp_domain_root_path+subdir['dir']+"/"+file, sub_path)
        else:
            # print(save_tmp_domain)
            process_article(subdir, sub_path)

def createFileDir(topic="RUS_UKR"):

    media_news_dir = '../media_statistic/mention/' + topic + '/source_url_domain_dict.json'

    
    with open(media_news_dir, 'r') as fp:
        medias = json.load(fp)
    medias = medias.keys()
    print(medias)
    save_dir = './' + topic + '/p_articles/'
    for ele in medias:
        if not os.path.exists(save_dir + ele + "/"):
            os.makedirs(save_dir + ele + "/")
    pass

if __name__ == "__main__":
    
    # topic = "RUS_UKR"
    # topic = "GBR_EUR"
    topic = "JPN_JPN"

    createFileDir(topic=topic)
    
    # sourcedir = 'C:\\Users\\corpaper\\Desktop\\merge_table_data\\' + topic + '\\huanran-articles\\'
    # sourcedir = 'C:\\Users\\corpaper\\Desktop\\merge_table_data\\' + topic + '\\jihe-articles\\'
    # sourcedir = 'C:\\Users\\corpaper\\Desktop\\merge_table_data\\' + topic + '\\jiale-articles\\'
    # sourcedir = 'C:\\Users\\corpaper\\Desktop\\merge_table_data\\' + topic + '\\shiyu-articles\\'
    sourcedir = 'C:\\Users\\corpaper\\Desktop\\merge_table_data\\JPN_JPN\\huanran-articles\\'
    

    domains = os.listdir(sourcedir)

    domains.reverse()
    
    for tmp_domain in domains:
        if tmp_domain in ["xxxxxx"]:
            process_domain_articles(tmp_domain, use_sub_dir=True, sourcedir=sourcedir, topic=topic)
        else:
            process_domain_articles(tmp_domain, use_sub_dir=False, sourcedir=sourcedir, topic=topic)
    
            
            
    pass