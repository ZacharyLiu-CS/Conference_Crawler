from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import re
import asyncio
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

async def downloadFile(paper_url:str):
    command = "wget {0} -P vldb_paper".format(paper_url)
    proc = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{command!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')


def extractFileName(paper_url:str):
    reg = re.compile(r"/[^/]+\.pdf")
    return re.findall(reg, paper_url)[-1]

async def getProjectNameAndUrl(paper_url):
    paper_name = extractFileName(paper_url)
    paper_path = "./vldb_paper{0}".format(paper_name)

    if not os.path.exists(paper_path):
        await downloadFile(paper_url=paper_url)
    project_url = extractFromPdf(paper_path)
    if project_url =="":
        return ("","")
    return (extractProjectName(project_url),project_url)

if '__name__' == '__main__':
    async def download_all_files():
        paper_url = "http://vldb.org/pvldb/vol14/p1311-suzuki.pdf"
        paper_url1 = "http://vldb.org/pvldb/vol14/p1-marcus.pdf"
        await asyncio.gather(downloadFile(paper_url),
        downloadFile(paper_url1))
    asyncio.run(download_all_files())

