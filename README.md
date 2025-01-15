# 项目说明

源于CVPR官网的搜索功能稀烂, 并且在论文列表中, 官网仅展示论文的标题。
如果使用F12进行关键字匹配的话, 则会丢失在摘要中有提及关键词, 而标题并没有显式表明任务的部分文章。
(例如pretrain的MAE叫Masked Autoencoders Are Scalable Vision Learners)

因此写本项目用来爬取cvpr等会议的accepted paper, 存储每一篇的标题+摘要。
查询基于标题+摘要的内容，可以多关键词检索。
筛选出的文章将按照标题+摘要的形式，用markdown给出。

## 环境配置

1. python3.9+
2. `pip install -r requirements.txt`

## 文件说明

1. `lib/`: 代码库, 包含了各种用到的类和函数。
2. `temp/`: 缓存文件夹。
3. `spider_run.py`: 调用对应的爬虫脚本, 实际上没有什么内容。
4. `export_markdown.py`: 按markdown格式导出按照关键词筛选后的文章信息, 包含标题,摘要,引用量。
5. `lib/spider_base.py`: 爬虫基类, 里面说明了要实现的函数, 引用量的爬取已实现, 通过selenium爬取谷歌学术。
6. `data.db`: 存储所有文章信息的数据库, 用sqlite访问。