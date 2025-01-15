import os
import requests
from bs4 import BeautifulSoup


from .spider_base import SpiderBase


class SpiderCVPR(SpiderBase):
    def __init__(self, conference:str, year:int, data_file="data.db"):
        super().__init__(conference, year, data_file)
    
        self.base_url = "https://openaccess.thecvf.com"

    def spider_all_paper_query_list(self) -> list[dict]:
        if not os.path.exists('temp/'):
            os.makedirs('temp/')
        if os.path.exists('temp/cvpr_{}.html'.format(self.year)):
            print("Loading from temp...")
            with open('temp/cvpr_{}.html'.format(self.year), 'r', encoding='utf8') as f:
                html = f.read()
        else:
            url = "https://openaccess.thecvf.com/CVPR{}?day=all".format(self.year)
            response = requests.get(url, headers=self.base_headers)
            response.raise_for_status()
            html = response.text
            with open('temp/cvpr_{}.html'.format(self.year), 'w', encoding='utf8') as f:
                f.write(html)
        soup = BeautifulSoup(html, "html.parser")

        paper_query_list = []
        container_div = soup.find("div", {"id": "content"})
        paper_div_list = container_div.find_all("dt", {"class": "ptitle"})
        for paper in paper_div_list:
            paper_name = paper.find("a").text.strip()
            href_url = paper.find("a").get("href")
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
        abstract = soup.find("div", {"id": "abstract"}).text.strip()
        return abstract