from Z_Services.SegmentServices import *
import sys
import io

def testFunc():
    try:
        report = {
            'dataTextID':,
            'dataImgID':
        }
        #Tìm textID và ImgID để tính toán
        currTextID = report['dataTextID']
        currImgID = report['dataImgID']
        #Lấy Img và Text để chấm
        text = evaluateStatus(currTextID)[0]
        img = evaluateStatus(currImgID)[0]
        #Dùng harmony để tính:
        harmony = {}
        fcount = 0
        score = 0
        for k in text.keys():
            if text[k]['status']==img[k]['status']:
                harmony[k] = {
                    "status": text[k]['status'],
                    "score": (text[k]['score']*img[k]['score']*2)/(text[k]['score']+img[k]['score'])
                }
                score += harmony[k]["score"]
            else:
                fcount +=1
                if text[k]['status'] == False:
                    harmony[k] = {
                        "status": False,
                        "score": (text[k]['score']*(1-img[k]['score'])*2)/(text[k]['score']+(1-img[k]['score']))
                    }
                    score += harmony[k]["score"]
                else:
                    harmony[k] = {
                        "status": False,
                        "score": ((1-text[k]['score'])*img[k]['score']*2)/((1-text[k]['score'])+img[k]['score'])
                    }
                    score += harmony[k]["score"]
        resEval = score/4
        if fcount < 2 and resEval > 0.8:
            report['qualified'] = True
            report['eval'] = resEval


    except Exception as e:
        print(e)
        return str(e), 500