#! python3
from re import L
import requests as re
from lxml import etree
import os
import re
import get_paper_list
from pdf_extractor import getProjectNameAndUrl

print("Begin of vldb crawler")
vldb21_page_cache = "./vldb21.html"
paper_list_page = ""
if os.path.exists(vldb21_page_cache):
    with open(vldb21_page_cache, mode='r') as f:
        paper_list_page = f.read()
else:
    vldb21_conference_url = "https://vldb.org/2021/?papers-research"
    req = re.get(vldb21_conference_url)
    req.close()
    paper_list_page = req.text
    with open(vldb21_page_cache, mode='w') as f:
        f.write(paper_list_page)

schedule_head_pattern = r'//*[@class="schedule-head"]/strong/text()'
schedule_item_pattern = r'//*[@class="schedule-item"]'

parser = etree.HTMLParser(encoding="utf-8")
f = open("paper.list",mode="w")
paper_tree = etree.parse(vldb21_page_cache, parser = parser)
session_entry = paper_tree.xpath(schedule_head_pattern)
paper_entry = paper_tree.xpath(schedule_item_pattern)
for paper_num in range(len(paper_entry)):
    session_text =paper_entry[paper_num].xpath('strong/@data-num')[0]
    session_num = int(float(session_text))-1
    if session_num >=16:
        session_num -= 1
    session_topic = session_entry[session_num].replace("\n"," ").replace("  ","")
    session_topic = re.sub("Research Session.+: ", "", session_topic).replace("I","").strip()
    paper_author =  paper_entry[paper_num].xpath('span[@class="schedule-item-people"]/span')[0].text.strip()
    author_entry = paper_entry[paper_num].xpath('span[@class="schedule-item-people"]/span[1]')[0]
    author_str = etree.tostring(author_entry, pretty_print=True).decode().strip().replace("\n"," ").replace("  ","").replace("(","").replace(")","").replace(",","")
    paper_unit = re.sub("<span.+</span>","", author_str)
    author_info = "{0}, {1}; et al.".format(paper_author,paper_unit)
    paper_title = paper_entry[paper_num].xpath('strong')[0].text.replace("\n"," ").replace("  ","").strip()
    paper_url = paper_entry[paper_num].xpath('strong/i/a/@href')[0]
    paper_project = getProjectNameAndUrl(paper_url=paper_url)
    f.write("{0}|{1}|{2}|{3}|{4}|{5}\n".format(session_topic, paper_title, author_info, paper_url,paper_project[0], paper_project[1]))
f.close()
'''
i = 1
for session_titile in session_entry:
    if i == 15:
       i+=1 
    print("session {0} = {1}".format(i, session_titile) )
    i += 1

'''