import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
from pymongo import MongoClient
from urllib.parse import urljoin
from urllib.parse import urljoin, quote
from DatabaseManager import DatabaseManager

class Spider:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.db_manager = DatabaseManager()

    def initialize_spider(self):
        pass

    def crawl_parent_page(self, url):
        self.driver.get(url)
        time.sleep(5)
        html_content = self.driver.page_source

        soup = BeautifulSoup(html_content, 'html.parser')

        div_elements = soup.find_all('div', class_='info-wrapper')
        type_info_list = []
        for div_element in div_elements:
            # 获取分类信息
            footer_info_div = div_element.find('div', class_='footer-info')
            type_info = "general"  # 默认为general分类
            if footer_info_div:
                p_tag = footer_info_div.find('p', class_='cate')
                if p_tag:
                    type_info = p_tag.text.strip()

            type_info_list.append(type_info)

        return html_content, type_info_list

    def crawl_child_page(self, url):
        self.driver.get(url)
        time.sleep(5)
        html_content = self.driver.page_source
        return html_content

    def extract_child_page_url(self, div_element, base_url):
        link_element = div_element.find('a', href=True)
        if link_element:
            child_url = link_element['href']
            if child_url:
                child_url = urljoin(base_url, child_url)  # 补全链接
            return child_url
        return None

    def extract_data(self, html_content, url):
        soup = BeautifulSoup(html_content, 'html.parser')
        title_element = soup.find('div', class_='detail-title')
        title = title_element.text.strip() if title_element else None

        content_element = soup.find('div', class_='detail htmlstr-wrapper')
        paragraphs = content_element.find_all(['p', 'a', 'img'])

        content = ""
        image_links = []
        for p in paragraphs:
            if p.name == 'img':
                # 图片标记
                img_url = p.get('src')
                if img_url and re.match(r'https://webdoc.lenovo.com.cn/lenovowsi/ts/.*', img_url):
                    content += "{img:" + img_url + "}"
                    image_links.append(img_url)
            elif p.name == 'a':
                # 文字链接标记
                link_text = p.text.strip()
                link_url = p.get('href')
                if link_url:
                    absolute_url = urljoin(url, link_url)
                    content += "{text:" + link_text + ", link:" + absolute_url + "} "
            elif p.name == 'p':
                # 普通段落
                text = p.text.strip()
                content += text + "\n"  # 添加换行符

        return title, content, image_links

    def run(self, url):
        try:
            loaded_urls = set()
            loaded_count = 0
            while True:
                html_content, type_info_list = self.crawl_parent_page(url)
                div_elements = BeautifulSoup(html_content, 'html.parser').find_all('div', class_='info-wrapper')
                new_loaded_count = 0

                for i, div_element in enumerate(div_elements):
                    child_url = self.extract_child_page_url(div_element, url)
                    print("子页面链接：", child_url)  # 调试输出
                    if child_url not in loaded_urls:
                        child_html_content = self.crawl_child_page(child_url)
                        title, content, image_links = self.extract_data(child_html_content, child_url)

                        # 获取当前问题的分类信息
                        type_info = type_info_list[i]

                        # 将数据插入 MongoDB，检查标题和来源是否重复
                        if title and child_url and not self.db_manager.collection.find_one(
                                {"title": title, "source": child_url}):
                            data = {
                                "title": title,
                                "source": child_url,
                                "type": type_info,  # 添加分类信息
                                "content": content,
                                "image_links": image_links
                            }
                            self.db_manager.insert_data(data)

                        loaded_urls.add(child_url)
                        new_loaded_count += 1

                if new_loaded_count == 0:
                    # 如果没有新加载的问题，说明已经到达页面底部，停止循环
                    break

                loaded_count += new_loaded_count
                if loaded_count >= 10:
                    # 如果已经加载了10个问题，停止继续加载，不再滚动页面
                    break

                # 模拟鼠标滚轮滑动，间隔时间可适当调整
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

        except KeyboardInterrupt:
            print("程序手动终止")
        finally:
            self.driver.quit()
            self.db_manager.close_connection()