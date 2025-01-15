import re
import os
import time
import sqlite3
import traceback
import requests
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


class SpiderBase:
    def __init__(self, conference:str, year:int, data_file="data.db"):
        self.conference = conference.lower()
        self.year = int(year)
        self.data_file = data_file
        
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        }
        
        # option = Options()
        # option.add_argument("--disable-features=OptimizationGuideModelDownloading,OptimizationHintsFetching,OptimizationTargetPrediction,OptimizationHints")
        # option.add_experimental_option("detach", True)
        # option.add_experimental_option("excludeSwitches", ['enable-automation'])
        # option.add_experimental_option('useAutomationExtension', False)
        # option.add_argument('--disable-blink-features=AutomationControlled')
        # option.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        # self.driver=webdriver.Chrome(options=option)
        # self.driver.set_window_position(20, 20)
        # self.driver.set_window_size(600, 900)
        # self.driver.set_page_load_timeout(80)
        # self.driver.get("https://scholar.google.com/scholar")

        if not os.path.exists(data_file):
            raise Exception("数据库文件不存在, 请先create_db.py")
        self.conn = self._connect2db()

        # 仅针对当前要爬取的当年会议, 不包含其他的会议
        self.exist_paper_name_list = self.get_exist_paper_from_db()

    def _connect2db(self):
        # 建立数据库连接
        conn = sqlite3.connect(self.data_file)
        return conn
        
    def get_exist_paper_from_db(self):
        # 读取paper表中已经爬取好的数据
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM paper WHERE conference=? AND year=?", (self.conference, self.year))
        papers = cursor.fetchall()
        exist_paper_name_list = [paper[0] for paper in papers]
        return exist_paper_name_list
    
    def insert_paper2db(self, paper_name:str, conference:str, year:int, abstract:str, citation:int):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO paper (paper_name, conference, year, abstract, citation) VALUES (?,?,?,?,?)", (paper_name, conference, year, abstract, citation))
        self.conn.commit()

    def run_spider(self, interval:int=5):
        """执行爬虫的主程序"""
        print("获取所有论文的索引数据...")
        paper_query_list = self.spider_all_paper_query_list()
        print("获取完成, 共有{}篇论文, 其中已爬取完成{}篇".format(len(paper_query_list), len(self.exist_paper_name_list)))
        print("开始每篇的摘要爬取...")
        
        error_num = 0
        for paper_query_info in tqdm(paper_query_list):
            if paper_query_info["paper_name"] in self.exist_paper_name_list:
                continue
            try:
                time.sleep(interval)
                abstract = self.spider_single_paper_abstract(paper_query_info)
                citation = self.spider_single_paper_citation(paper_query_info["paper_name"])
                self.insert_paper2db(paper_query_info["paper_name"], self.conference, self.year, abstract, citation)
                error_num = 0
            except:
                error_num += 1
                traceback.print_exc()
            if error_num > 5:
                break
        self.exist_paper_name_list = self.get_exist_paper_from_db()
        print("爬取完成, 共有{}篇论文, 其中已爬取完成{}篇".format(len(paper_query_list), len(self.exist_paper_name_list)))


    def spider_all_paper_query_list(self) -> list[dict]:
        """获取当前会议所有的paper对应查询所需要的data, 至少包含paper_name字段"""
        raise NotImplementedError
    
    def spider_single_paper_abstract(self, query_data:dict) -> str:
        """获取单个paper的摘要"""
        raise NotImplementedError
    
    def spider_single_paper_citation(self, paper_name:str) -> int:
        """获取单个paper的引用次数"""
        WebDriverWait(self.driver, 3600).until(
            EC.presence_of_element_located((By.ID, 'gs_hdr_tsi'))
        )
        time.sleep(2)
        self.driver.find_element(By.ID, 'gs_hdr_tsi').clear()
        self.driver.find_element(By.ID, 'gs_hdr_tsi').send_keys(paper_name)
        self.driver.find_element(By.ID, "gs_hdr_tsb").click()
        
        flag = False
        for _ in range(10):
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'gs_res_ccl_mid'))
                )
                element = self.driver.find_element(By.ID, "gs_res_ccl_mid")
                if paper_name.split(' ')[0].lower() in element.text.lower() or paper_name.split(' ')[-1].lower() in element.text.lower():
                    flag = True
                    break
                time.sleep(2)
            except:
                time.sleep(3)
                continue
        if flag is False:
            raise ElementError("加载新引用页面失败")

        # 找所有论文的总列表
        table_div = self.driver.find_element(By.ID, "gs_res_ccl_mid")
        if table_div is None:
            with open("temp/{}.html".format(paper_name.replace(' ', '_')), "w", encoding="utf8") as f:
                f.write(self.driver.page_source)
            raise ElementError("找不到论文总列表")

        # 找第一篇论文的信息div
        citation_div = table_div.find_element(By.XPATH, "//div[@class='gs_fl gs_flb']")
        citation_info_list = citation_div.find_elements(By.TAG_NAME, "a")
        
        citation = 0
        keyword = "引用次数"
        for info in citation_info_list:
            if keyword in info.text:
                citation = int(re.findall(r"\d+", info.text)[0])
                break
        return citation
    

class ElementError(Exception):
    ...