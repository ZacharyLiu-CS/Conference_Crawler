#! python3
from re import L
from lxml import etree
import os
import re
import requests
from pdf_extractor import getProjectNameAndUrl
import asyncio
print("Begin of vldb crawler")
vldb21_page_cache = "./vldb21.html"
paper_list_page = ""
if os.path.exists(vldb21_page_cache):
    with open(vldb21_page_cache, mode='r') as f:
        paper_list_page = f.read()
else:
    vldb21_conference_url = "https://vldb.org/2021/?papers-research"
    req = requests.get(vldb21_conference_url)
    req.close()
    paper_list_page = req.text
    with open(vldb21_page_cache, mode='w') as f:
        f.write(paper_list_page)

schedule_head_pattern = r'//*[@class="schedule-head"]/strong/text()'
schedule_item_pattern = r'//*[@class="schedule-item"]'

parser = etree.HTMLParser(encoding="utf-8")
f = open("paper.list",mode="w")
paper_tree = etree.parse(vldb21_page_cache, parser = parser)
session_entries = paper_tree.xpath(schedule_head_pattern)
paper_entries = paper_tree.xpath(schedule_item_pattern)

async def get_one_paper_entry(paper_entry, session_entries):
    session_text =paper_entry.xpath('strong/@data-num')[0]
    session_num = int(float(session_text))-1
    if session_num >=16:
        session_num -= 1
    session_topic = session_entries[session_num].replace("\n"," ").replace("  ","")
    session_topic = re.sub("Research Session.+: ", "", session_topic).replace("I","").strip()
    paper_author =  paper_entry.xpath('span[@class="schedule-item-people"]/span')[0].text.strip()
    author_entry = paper_entry.xpath('span[@class="schedule-item-people"]/span[1]')[0]
    author_str = etree.tostring(author_entry, pretty_print=True).decode().strip().replace("\n"," ").replace("  ","").replace("(","").replace(")","").replace(",","")
    paper_unit = re.sub("<span.+</span>","", author_str)
    author_info = "{0}, {1}; et al.".format(paper_author,paper_unit)
    paper_title = paper_entry.xpath('strong')[0].text.replace("\n"," ").replace("  ","").strip()
    paper_url = paper_entry.xpath('strong/i/a/@href')[0]
    paper_project = await getProjectNameAndUrl(paper_url=paper_url)
    f.write("{0}|{1}|{2}|{3}|{4}|{5}\n".format(session_topic, paper_title, author_info, paper_url,paper_project[0], paper_project[1]))

async def main_loop(): 
    coros=[get_one_paper_entry(paper_entry, session_entries)for paper_entry in paper_entries]
    await asyncio.gather(*coros, return_exceptions=True)
asyncio.run(main_loop())
f.close()