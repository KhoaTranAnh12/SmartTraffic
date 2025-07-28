#Công An
from EvaluationLib.image.lib.AITrain import *
from ultralytics import YOLO
import cv2
from dotenv import *
import os
def TestForPolices(img):
    load_dotenv()
    model = YOLO(os.getenv('IMGMODEL') + 'police_best.pt')
    results = model.predict(img,conf=0.25)
    negativeConfSummary = 1
    negativeConfLowest = 1
    results[0].show()
    for det in results[0].boxes:
        conf = det.conf.item()  # Confidence score của bounding box
        negativeConfSummary *=(1-conf)
        if negativeConfLowest > 1-conf: negativeConfLowest = 1-conf
    resNeg = (negativeConfSummary + negativeConfLowest)/2
    if(resNeg>0.5):
        return (False, round(resNeg,2))
    else:
        return (True, round(1-resNeg,2))
#Kẹt xe
def TestForTJam(img):
    device = 'cpu'
    classes = [False,True] #['not trafffic jam','traffic jam']
    res = AITrain.ResNetTest(os.getenv('IMGMODEL') + 'bestTrafficJamModel.pth',img,classes)
    return res
#Vật cản
def TestForObstacles(img):
    model = YOLO(os.getenv('IMGMODEL') + "obstacles.pt")
    results = model.predict(img,conf=0.25)
    negativeConfSummary = 1
    negativeConfLowest = 1
    for det in results[0].boxes:
        conf = det.conf.item()  # Confidence score của bounding box
        negativeConfSummary *=(1-conf)
        if negativeConfLowest > 1-conf: negativeConfLowest = 1-conf
    resNeg = (negativeConfSummary + negativeConfLowest)/2
    if(resNeg>0.5):
        return (False, round(resNeg,2))
    else:
        return (True, round(1-resNeg,2))
#Ngập
def TestForFlooded(img):
    device = 'cpu'
    classes = [True,False] #['flooded','not flooded']
    res = AITrain.ResNetTest(os.getenv('IMGMODEL') + 'Flooded-classification.pth',img,classes)
    return res

#Status: Text Với img gần tương đương nhau. (true, true, false, true) (true, true, true, false)

#Text: 0.85 Img: 0.8 -> Ok
#Text: 0.7 Img: 0.9 -> Thuộc diện xem xét lại


#Có trang admin. Monitor liên quan đến data.

#(policeEval,obstaclesEval,trafficJamEval,floodedEval,'text')
#Giao ra được cái tuple 4 thành phần: ((Status của police, confScore của police), (Status của obstacles, eval của obstacles), (Status của Tjam, eval của Tjam), (Status của flooded, eval của flooded), 'text')

