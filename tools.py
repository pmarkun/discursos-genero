import html2text
from rtf import Rtf2Html
import pymongo

def rtf2md(rtfstring):
    """Converts rtf to markdown file"""
    tmp_html = Rtf2Html.getHtml(rtfstring)
    tmp_markdown = html2text.html2text(tmp_html)
    return tmp_markdown

def yieldDb(items):
    """Dumb Yield helper function"""
    for item in items:
        yield item
            
def loadDb(items, db, collection):
    """Load a dictionary in a specific mongo database collection"""
    for item in yieldDb(items):
        db[collection].update({"id" : item["id"]}, item,  True)
