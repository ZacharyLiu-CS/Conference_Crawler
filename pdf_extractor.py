from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import re
import os

def extractFromPdf(pdf_path:str):
    output_string = StringIO()
    with open(pdf_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
            break
    reg = re.compile(r"\nPVLDB Artifact Availability:\n.+\nhttps.+\n")
    matches = re.findall(reg, output_string.getvalue())
    if len(matches) == 0:
        return ""
    else:
        reg_url = re.compile(r"http.+\n")
        url_list = re.findall(reg_url, matches[0])
        return url_list[0].replace("\n","")

def extractProjectName(project_url:str):
    reg = re.compile(r"/[^/]+\.")
    return re.findall(reg, project_url)[-1][1:-1]

def downloadFile(paper_url:str):
    os.system("wget {0} -P vldb_paper".format(paper_url))

def extractFileName(paper_url:str):
    reg = re.compile(r"/[^/]+\.pdf")
    return re.findall(reg, paper_url)[-1]

def getProjectNameAndUrl(paper_url):
    paper_name = extractFileName(paper_url)
    paper_path = "./vldb_paper{0}".format(paper_name)


    if not os.path.exists(paper_path):
        downloadFile(paper_url=paper_url)
    project_url = extractFromPdf(paper_path)
    if project_url =="":
        return ("","")
    return (extractProjectName(project_url),project_url)

paper_url = "http://vldb.org/pvldb/vol14/p1311-suzuki.pdf"
paper_url1 = "http://vldb.org/pvldb/vol14/p1-marcus.pdf"
print(getProjectNameAndUrl(paper_url1))