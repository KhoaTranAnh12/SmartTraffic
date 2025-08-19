from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline, logging

logging.set_verbosity_error()

def JamTest(text: str):
    jam_model_dir="../models/trafficjam-model"
    tokenizer = AutoTokenizer.from_pretrained(jam_model_dir)
    model = AutoModelForTokenClassification.from_pretrained(jam_model_dir)
    ner_pipeline_obj = pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple"
    )
    results = ner_pipeline_obj(text)
    # jam_results = [r for r in results if r["entity_group"].upper() == "JAM"]
    jam_results = [r for r in results if "JAM" in r["entity_group"].upper()]
    if jam_results:
        result = max(jam_results, key=lambda x: x["score"])
        return result["score"]
    else:
        return 0
    
def PoliceTest(text: str):
    police_model_dir = "../models/police-model"
    tokenizer = AutoTokenizer.from_pretrained(police_model_dir)
    model = AutoModelForTokenClassification.from_pretrained(police_model_dir)
    ner_pipeline_obj = pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple"
    )
    results = ner_pipeline_obj(text)
    # police_results = [r for r in results if r["entity_group"].upper() == "POLICE"]
    police_results = [r for r in results if "POLICE" in r["entity_group"].upper()]
    if police_results:
        result = max(police_results, key=lambda x: x["score"])
        return result["score"]
    else:
        return 0
    
def TotalTest(text: str):
    model_dir = "../models/model-total"
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    ner_pipeline_obj = pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple"
    )
    
    results = ner_pipeline_obj(text)

    target_tags = ["VELOCITY", "LOCATION"]
    
    output = {}
    
    for tag in target_tags:
        tag_results = []
        for r in results:
            entity = r["entity_group"].upper()
            if entity.startswith("B-") or entity.startswith("I-"):
                entity = entity.split("-")[-1]
            if entity == tag:
                tag_results.append(r)
        
        if tag_results:
            best = max(tag_results, key=lambda x: x["score"])
            output[tag] = {
                "text": best["word"],
                "score": float(best["score"])
            }
        else:
            output[tag] = {"text": None, "score": 0.0}
    
    return output
    
if __name__ == "__main__":
    jam_test_texts = [
        "Đường Nguyễn Văn Cừ đang kẹt xe nặng.",
        "Trên Quốc Lộ 1A bị ùn tắc một đoạn 2km.",
        "Giao thông thông thoáng ở nội thành."
    ]
    
    pol_test_texts = [
        "Cảnh sát đang tuần tra quanh khu vực Hồ Gươm.",  
        "Công an vừa kiểm tra giấy tờ các phương tiện trên đường Láng.",  
        "Lực lượng cảnh sát giao thông đang điều tiết tại ngã tư Cầu Giấy.", 
    ]
    
    total_test_texts = [
        "Xe đang chạy với tốc độ 60 km/h tại Hà Nội",
        "Tốc độ xe khoảng 40 km/h trên Quốc Lộ 1A, gần TP. Hồ Chí Minh",
        "Ô tô di chuyển chậm 20 km/h quanh cầu Chương Dương, Hà Nội",
        "Xe tải đi với vận tốc 30 km/h tại đường Trần Hưng Đạo, TP. Hải Phòng"
    ]


    for text in jam_test_texts:
        score = JamTest(text)
        print(f"Text: {text}\nJam score: {score}\n")
        
    for text in pol_test_texts:
        score = PoliceTest(text)
        print(f"Text: {text}\nPolice score: {score}\n")
    
    for text in total_test_texts:
        result = TotalTest(text)
        print(f"Text: {text}\nTotal result: {result}\n")