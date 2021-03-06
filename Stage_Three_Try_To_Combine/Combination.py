from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
import re
import requests
import os
import cv2
import os.path
from PIL import Image

NameList = []
PictureNumber = 1
MainPage = 'https://zh.moegirl.org.cn/Mainpage'
HomePage = 'https://zh.moegirl.org.cn'
SearchPageBase = 'https://zh.moegirl.org.cn/index.php?'
numberOfPictures = 0
MaxNum = 100


def isPictureUrl(URL, urlForCheck):
    url = str(URL.encode())
    if '\\x' in url:
        print("NotRight" + str(url) + "NotRight")
        return False
    if 'thumb' in url:
        return False
    if 'px' in URL and 'px' in urlForCheck:
        if URL[:URL.rfind('/')] == urlForCheck[:urlForCheck.rfind('/')]:
            return int(URL[URL.rfind('/') + 1:URL.rfind('px')]) > int(
                urlForCheck[urlForCheck.rfind('/') + 1:urlForCheck.rfind('px')])
    return True


def createFile(thisName):
    Path = os.getcwd() + '\\' + thisName + '\\'
    if not os.path.exists(Path):
        os.mkdir(Path)
    return Path


def savePicture(IMAGE, num, Name, Location):
    PictureName = Location + Name + str(num) + '.png'
    fp = open(PictureName, 'wb')
    fp.write(IMAGE)
    fp.close()
    print("Saving '"+str(Name+str(num)) + "' to " + Location + "\n")
    NameList.append(PictureName)


def getHtml(url):
    return urlopen(url)


def getBs(html):
    return BeautifulSoup(html, 'lxml')


def getContent(url):
    return requests.get(url).content


def getNewUrl(url):
    if 'https://' in url:
        return url
    else:
        return HomePage + url


def getPicture(UrlList, tag, div, num, rec):
    NewNum = 1
    LinkList = []
    url_Basic = HomePage
    if num == -1:
        return
    for url in UrlList:
        bs = getBs(getHtml(url))
        for Link in bs.find_all(tag, {div: rec}):
            newUrl = getNewUrl(Link.attrs[div])
            if 'File' in newUrl or newUrl in LinkList:
                continue
            if isPictureUrl(newUrl, url_Basic):
                LinkList.append(newUrl)
                pic = getContent(newUrl)
                print("Downloading " + newUrl)
                savePicture(pic, NewNum, 'Downloaded_Picture', createFile('Picture'))
                NewNum += 1
                url_Basic = newUrl
                if NewNum > MaxNum:
                    return


def getPictureUrl(tag, div1, rec, bs):
    LIST = []
    List_Number = -1
    for Link in bs.find_all(tag, {div1: rec}):
        if div1 in Link.attrs:
            newUrl = getNewUrl(Link.attrs[div1])
            if newUrl in LIST:
                continue
            else:
                List_Number += 1
                LIST.append(newUrl)
    getPicture(LIST, tag, div1, List_Number, rec)


def detect(filename, cascade_file="FaceDetect.xml"):
    global PictureNumber
    if not os.path.isfile(cascade_file):
        raise RuntimeError("%s: not found" % cascade_file)

    cascade = cv2.CascadeClassifier(cascade_file)
    image_Original = Image.open(filename)
    image = cv2.imread(filename, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = cascade.detectMultiScale(gray,
                                     # detector options
                                     scaleFactor=1.1,
                                     minNeighbors=5,
                                     minSize=(24, 24))
    i = 1
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        image_Cropped = image_Original.crop((x, y, x + w, y + h))
        image_Cropped.save(createFile('Faces') + 'Face' + str(PictureNumber) + '.png')
        PictureNumber += 1
        i += 1

    if i == 1:
        cv2.imshow("OriginalFace", image)
        cv2.waitKey(0)
        return
    cv2.imshow("AnimeFaceDetect", image)
    cv2.waitKey(0)


def makeSearchedPage(search):
    ReturnUrl = SearchPageBase + 'search=' + str(search) + '&title=Special'
    return ReturnUrl


def repairName(Name):
    EncodeName = str(Name.encode())
    if '\\' not in EncodeName:
        Name = Name.replace(' ', '+')
    else:
        Name = quote(Name, encoding='GBK')
    return Name


def getFirstResult(url):
    html = urlopen(url)
    bs = BeautifulSoup(html, 'lxml')
    status = bs.find('a', {'data-serp-pos': '0'})
    if status is None:
        print("We have not find any Results.\nPlease Try again.")
        return None
    link = status.attrs['href']
    StartUrl = HomePage + link
    return StartUrl


def ifResults(url):
    bs = getBs(getHtml(url))
    status = bs.find('a', {'data-serp-pos': '0'})
    if status is None:
        return False
    return True


def main():
    print("Dear Sir/Madam:")
    print("All the pictures will be downloaded from \n" + MainPage)
    print("Please, feel free to type in the character you want:")
    NameOfCharacter = input("(Type in a character.)\n")
    print("Now, I'll try to download the pictures of '" + NameOfCharacter + "'")
    NameOfCharacter = repairName(NameOfCharacter)
    InitialUrl = makeSearchedPage(NameOfCharacter)
    if ifResults(InitialUrl):
        url_HomePage = getFirstResult(InitialUrl)
    else:
        url_HomePage = InitialUrl
    if url_HomePage is None:
        exit(0)
    print("Looking into website " + url_HomePage)
    html1 = urlopen(url_HomePage)
    bs1 = BeautifulSoup(html1, 'lxml')
    global MaxNum
    MaxNum = int(input("How many pictures do you want to download 'at most'?\n(Please type a number.)\n"))
    getPictureUrl('a', 'href', re.compile('\.(jpg|png)$'), bs1)
    numberOfPictures = len(NameList)
    print("We've downloaded " + str(numberOfPictures) + " pictures.")
    print("How many pictures do you want me to handle?")
    TotalNum = int(input("(Type in a number less than " + str(numberOfPictures) + ".)\n"))
    if numberOfPictures == 0:
        print("Thanks for Using this programme.\nLooking forward to meeting you again!")
        exit(0)

    total = 0
    for name in NameList:
        total += 1
        detect(name)
        if total >= TotalNum:
            break

    if numberOfPictures == 1:
        print("The Picture is now in file 'Picture' and 'Faces'")
    else:
        print("All the Pictures are now in 'Picture' and 'Faces'")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print("Error")
    finally:
        print("Thanks for Using this programme.\nLooking forward to meeting you again!")
