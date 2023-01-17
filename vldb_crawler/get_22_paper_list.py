#! python3
from re import L
from lxml import etree
import os
import re
import requests
from pdf_extractor import getProjectNameAndUrl
import asyncio
print("Begin of vldb crawler")
vldb21_page_cache = "./vldb22.html"
paper_list_page = ""
if os.path.exists(vldb21_page_cache):
    with open(vldb21_page_cache, mode='r') as f:
        paper_list_page = f.read()
else:
    vldb21_conference_url = "http://vldb.org/pvldb/volumes/15#issue-11"
    req = requests.get(vldb21_conference_url)
    req.close()
    paper_list_page = req.text
    with open(vldb21_page_cache, mode='w') as f:
        f.write(paper_list_page)


parser = etree.HTMLParser(encoding="utf-8")
f = open("paper.list", mode="w")
paper_tree = etree.parse(vldb21_page_cache, parser=parser)
paper_entries_num = 75
item_pattern = r'//*[@id="issue-11"]/div[5]/div[{0}]'
# //*[@id="issue-11"]/div[5]/div[1]/div/h5


async def get_one_paper_entry(paper_entry_num, item_pattern, paper_tree):
    # print(paper_entry_num)
    item_pattern = item_pattern.format(paper_entry_num)
    temp_pattern = item_pattern + "/div/h5/text()"
    paper_tittle = paper_tree.xpath(temp_pattern)[0]

    author_pattern = item_pattern + "/div/p[2]/text()"
    paper_author = paper_tree.xpath(author_pattern)

    paper_first_author = paper_author[0].split(';')[0] + "; et al."
    paper_first_author = paper_first_author.replace(" (", ", ").replace(")","").replace("*","")

    paper_url_pattern = item_pattern + "/div/div[4]/a/@href"
    paper_url = paper_tree.xpath(paper_url_pattern)[0]

    artifact_pattern = item_pattern + "/div/div[4]/img"
    artifact_res = False if paper_tree.find(artifact_pattern) == None else True
    if ( artifact_res == False):
        return


    paper_project = await getProjectNameAndUrl(paper_url=paper_url)
    f.write("{0}|{1}|{2}|{3}\n".format( paper_tittle, paper_first_author, paper_url, paper_project[1]))

#     session_num = int(float(session_text))-1
#     if session_num >=16:
#         session_num -= 1
#     paper_author =  paper_entry.xpath('span[@class="schedule-item-people"]/span')[0].text.strip()
#     author_entry = paper_entry.xpath('span[@class="schedule-item-people"]/span[1]')[0]
#     author_str = etree.tostring(author_entry, pretty_print=True).decode().strip().replace("\n"," ").replace("  ","").replace("(","").replace(")","").replace(",","")
#     paper_unit = re.sub("<span.+</span>","", author_str)
#     author_info = "{0}, {1}; et al.".format(paper_author,paper_unit)
#     paper_title = paper_entry.xpath('strong')[0].text.replace("\n"," ").replace("  ","").strip()
#     paper_url = paper_entry.xpath('strong/i/a/@href')[0]
#     paper_project = await getProjectNameAndUrl(paper_url=paper_url)
#     f.write("{0}|{1}|{2}|{3}|{4}\n".format( paper_title, author_info, paper_url,paper_project[0], paper_project[1]))


async def main_loop():
    coros = [get_one_paper_entry(paper_entry, item_pattern, paper_tree)
             for paper_entry in range(1, paper_entries_num+1)]
    await asyncio.gather(*coros, return_exceptions=True)
asyncio.run(main_loop())
f.close()
