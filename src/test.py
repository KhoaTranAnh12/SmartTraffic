from EvaluationLib.main import *
from EvaluationLib.image.lib.AITest import *
from dotenv import *
from bson import ObjectId
from datetime import datetime
import os
from dotenv import *
def evaluateStatus(data):
    try:
        if data['type'] == 'image':
            policeEval = TestForPolices('C:/Users/Administrator/OneDrive/Desktop/DACN-DATN/SmartTraffic-BE/aaaaa.jpg')
            obstaclesEval = TestForObstacles('C:/Users/Administrator/OneDrive/Desktop/DACN-DATN/SmartTraffic-BE/aaaaa.jpg')
            trafficJamEval = TestForTJam('C:/Users/Administrator/OneDrive/Desktop/DACN-DATN/SmartTraffic-BE/aaaaa.jpg')
            floodedEval = TestForFlooded('C:/Users/Administrator/OneDrive/Desktop/DACN-DATN/SmartTraffic-BE/aaaaa.jpg')
            return (policeEval,obstaclesEval,trafficJamEval,floodedEval,'text')
        elif data['type'] == 'text':
            policeEval = EvaluateRandomExample()
            obstaclesEval = EvaluateRandomExample()
            trafficJamEval = EvaluateRandomExample()
            floodedEval = EvaluateRandomExample()
            return (policeEval,obstaclesEval,trafficJamEval,floodedEval,'img')
    except Exception as e:
        print(e)
        return str(e), 500


data =  {
    '_id': ObjectId('aaaaaaaaaaaaaaaaaaaaaaaa'),
    'type': 'text',
    'infoID': ObjectId('abcdabcdabcdabcdabcdabcd'),
    'uploadTime': datetime.date(datetime.now()),
    'processed': False
}

text = {
    'dataID': ObjectId('abcdabcdabcdabcdabcdabcd'),
    'source': 'test.txt'
}


print(evaluateStatus(data))
# load_dotenv()
# # print(os.getenv('STORAGE') + '../storage/images/unverified')
# print(os.listdir(os.getenv('STORAGE') + '/images/unverified'))