import os
import sqlite3


def get_paper_from_db(conference, year):
    # Connect to the database
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM paper WHERE conference=? AND year=?", (conference, year))
    papers = cursor.fetchall()
    paper_data_list = [{
        "paper_name": paper[0],
        "conference": paper[1],
        "year": paper[2],
        "abstract": paper[3],
        "citation": paper[4]
    } for paper in papers]
    conn.close()
    return paper_data_list

def filter_for_paper(paper_data_list, keyword_list, select_from_abstract=False):
    """最基本的, 有出现关键词则match的检索策略"""
    filtered_papers = []
    for paper in paper_data_list:
        query_data = paper["paper_name"].lower()
        if select_from_abstract:
            query_data += paper["abstract"].lower()
        for keyword in keyword_list:
            if keyword in query_data:
                filtered_papers.append(paper)
                break
    filtered_papers.sort(key=lambda paper: paper["citation"], reverse=True)
    return filtered_papers

if __name__ == '__main__':
    conference = "cvpr".lower()
    year = 2024
    keyword_list = ["pre-train", "pretrain", "unsupervise", "autoencoder", "self-supervise"]

    filtered_papers = filter_for_paper(get_paper_from_db(conference, year), keyword_list)
    with open("export_{}_{}_{}.md".format(conference, year, "_".join(keyword_list)), "w") as f:
        for index, paper in enumerate(filtered_papers):
            f.write("## {}. {}\n\n引用量:{}\n\n摘要:{}\n\n".format(index, paper["paper_name"], paper["citation"], paper["abstract"]))