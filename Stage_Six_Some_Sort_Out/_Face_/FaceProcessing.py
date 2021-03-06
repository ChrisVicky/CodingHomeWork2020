import cv2
import os.path
from PIL import Image
import time


def BarSimulator(PictureName):
    NUM = 100
    for k in range(1, NUM + 1):
        print('\r' + '[正在处理 %s 中]:%s %d%%' % (PictureName, '#' * int(50 * k / NUM), int(100 * float(k) / float(NUM))),
              end='')
        time.sleep(0.001)
    print()


def FaceProcess(number, TotalNumber, PictureName, ImageFile, cascade_file="_Face_\DetectFace.xml"):
    FileSaveName = os.getcwd() + '\Results' + '\Face'
    print("[处理 %s 中][第 %d 张 / 共 %d 张]" % (PictureName, number, TotalNumber))
    if not os.path.exists(FileSaveName):
        os.makedirs(FileSaveName)
    if not os.path.isfile(cascade_file):
        raise RuntimeError("%s: not found" % cascade_file)
    cascade = cv2.CascadeClassifier(cascade_file)
    image_original = Image.open(ImageFile)
    image = cv2.imread(ImageFile, cv2.IMREAD_COLOR)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.equalizeHist(gray_image)
    faces = cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100),)
    BarSimulator(PictureName)
    i = 1
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        Face_Path = FileSaveName + '\\' + PictureName[:PictureName.rfind('.jpg')] + '_Face_'+str(i)+'.jpg'
        image_original.crop((x, y, x+w, y+h)).save(Face_Path)
        i += 1
    print("[%s处理完成，检测到到%d张脸]\n" % (PictureName, len(faces)))


def Processing(subFile, Num):
    Path = os.getcwd() + '\Results' + subFile
    Picture_List = os.listdir(Path)
    i = 0
    for picture_name in Picture_List:
        if 'jpg' not in picture_name:
            continue
        path = Path + '\\' + picture_name
        i += 1
        if i > Num:
            return
        try:
            FaceProcess(i, Num, picture_name, path)
        except Exception as e:
            exit(e)


def test():
    test_file = 'C:\\Christopher\\TJU\\2020\\Classes\\3Coding\\FinaleWork\\PythonBasedAnimateFacesDetect\\CodingHomeWork2020\\Stage_Six_Some_Sort_Out\\_Face_\\2020-12-16'
    Picture_List = os.listdir(test_file)
    Num = len(Picture_List)
    i = 0
    for picture_name in Picture_List:
        if 'jpg' not in picture_name:
            continue
        path = test_file + '\\' + picture_name
        i += 1
        if i > Num:
            return
        try:
            FaceProcess(i, Num, picture_name, path)
        except Exception as e:
            exit(e)
# test()
