import configparser
import requests
import time
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('config.ini')

base_url = "https://iknow.lenovo.com.cn/detail/321237?type=0&keyword=&keyWordId="
page_count = int(config['Spider']['page_count'])
delay = int(config['Spider']['delay'])

# 创建或打开文本文件
with open('data.txt', 'w') as file:
    # 循环获取页面内容
    for page in range(1, page_count + 1):
        url = f"{base_url}{page}"
        response = requests.get(url)

        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")
            questions = soup.find_all("div", class_="question")
            answers = soup.find_all("div", class_="answer")

            # 处理数据...
            for question, answer in zip(questions, answers):
                file.write(f"问题: {question.text}\n")
                file.write(f"答案: {answer.text}\n")

            # 添加延迟
            time.sleep(delay)
        else:
            print(f"请求第{page}页失败")
