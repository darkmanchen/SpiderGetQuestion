from spider import Spider

if __name__ == "__main__":
    url = "https://iknow.lenovo.com.cn/topic/ol_0x32c851a_0"
    spider_instance = Spider()
    spider_instance.initialize_spider()
    spider_instance.run(url)
