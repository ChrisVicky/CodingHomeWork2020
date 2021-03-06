from urllib.parse import quote
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
MoeGirlLink = 'https://zh.moegirl.org.cn'
SearchPageBase = 'https://zh.moegirl.org.cn/index.php?'
BaiduSearchBase = 'https://baike.baidu.com/search/none?word='
BaiduWikiBase = 'https://baike.baidu.com'


def makeSearchedPage(search):
    ReturnUrl = SearchPageBase + 'search=' + str(search) + '&title=Special'
    return ReturnUrl


def repairName(Name):
    EncodeName = str(Name.encode())
    # print("EncodeName " + EncodeName)
    if '\\' not in EncodeName:
        Name = Name.replace(' ', '+')
    else:
        Name = quote(Name, encoding='utf-8', errors='replace')
    return Name


def getResult(Name):
    name = repairName(Name)
    url = BaiduSearchBase + name
    html = urlopen(url)
    print("[SearchURL]:%s" % url)
    bs = BeautifulSoup(html, 'lxml')
    Link = bs.find('div', {'class': 'spell-correct'})
    if Link:
        return BaiduWikiBase + Link.find('a').attrs['href']
    status = bs.find('dl', {'class': 'search-list'})
    if status is None:
        if len(Name) >= 1:
            return getResult(Name[:len(Name)-1])
        print("We have not find any Results.\nPlease Try again.")
        return None
    link = status.find('dd').find('a').attrs['href']
    if 'https://' not in link:
        link = BaiduWikiBase + link
    return link


def findTag(url):
    print("[WikiURL]:%s" % url)
    html = urlopen(url)
    bs = BeautifulSoup(html, 'lxml')
    Temp = bs.find('br')
    if Temp is not None:
        Name = str(Temp.nextSibling)
        if Name is None:
            return Exception
        if re.match('[a-z]*', Name) is None:
            Name = str(Temp.nextSibling.nextSibling.nextSibling)
    else:
        Temp = bs.find('dt', {'class': 'basicInfo-item name'}, text='外文名')
        Temp = Temp.nextSibling.nextSibling
        Temp = str(Temp)
        print("TEMP " + Temp)
        if '(' in Temp:
            Name = Temp[Temp.rfind('(')+1:Temp.rfind(')')]
        else:
            Name = Temp[Temp.find('\n')+1:Temp.rfind('\n')]
    Tag = Name.replace(' ', '_')
    if '\n' in Tag:
        Tag = Tag[:Tag.rfind('\n')]
    Tag = Tag.upper()
    Tag = Tag.swapcase()
    print("[Tag]:%s" % Tag)
    return Tag


def FindPerson(name):
    try:
        return findTag(getResult(name))
    except Exception as e:
        exit(e)
# print(FindPerson('御坂琴'))
