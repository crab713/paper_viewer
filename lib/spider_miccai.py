import os
import re
import requests
from bs4 import BeautifulSoup


from .spider_base import SpiderBase


class SpiderMiccai(SpiderBase):
    def __init__(self, conference:str, year:int, data_file="data.db"):
        super().__init__(conference, year, data_file)
    
        if year == 2021:
            self.base_url = "https://miccai2021.org/openaccess/paperlinks"
        elif year == 2022:
            self.base_url = "https://conferences.miccai.org"
        elif year == 2023:
            self.base_url = "https://conferences.miccai.org"
        elif year == 2024:
            self.base_url = "https://papers.miccai.org"
        else:
            raise Exception("年份不适配")

    def spider_all_paper_query_list(self) -> list[dict]:
        if not os.path.exists('temp/'):
            os.makedirs('temp/')
        if os.path.exists('temp/miccai_{}.html'.format(self.year)):
            print("Loading from temp...")
            with open('temp/miccai_{}.html'.format(self.year), 'r', encoding='utf8') as f:
                html = f.read()
        else:
            url = self.base_url
            if self.year == 2022 or self.year == 2023:
                url = self.base_url + ('/' if self.base_url[-1] != '/' else '') + str(self.year) + "/papers/"
            elif self.year == 2024:
                url = self.base_url + ('/' if self.base_url[-1] != '/' else '') + "miccai-2024/"
            response = requests.get(url, headers=self.base_headers)
            response.raise_for_status()
            html = response.text
            with open('temp/miccai_{}.html'.format(self.year), 'w', encoding='utf8') as f:
                f.write(html)
        soup = BeautifulSoup(html, "html.parser")

        paper_query_list = []
        container_div = soup.find("div", {"class": "container-posts"})
        paper_div_list = container_div.find_all("ul", recursive=False)
        for paper in paper_div_list:
            if self.year in [2021, 2022, 2023]:
                paper_name = paper.find("a").text.strip()
                href_url = paper.find("a").get("href")
            elif self.year in [2024]:
                paper_name = paper.find("b").text.strip()
                href_url = paper.find("a", string="Paper Information and Reviews").get("href")
            paper_query_list.append({
                "paper_name": paper_name,
                "href_url": href_url
            })
        return paper_query_list
    
    def spider_single_paper_abstract(self, query_data:dict):
        url = self.base_url + ('/' if query_data["href_url"][0] != '/' else '') + query_data["href_url"]
        response = requests.get(url, headers=self.base_headers)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        abstract = soup.find("h1", {"id": "abstract-id"}).find_next("p").text.strip()
        return abstract