import sys
import pymongo
from pymongo.errors import PyMongoError
import osmium as o
from datetime import datetime
import time
import os
from dotenv import load_dotenv
class TrafficMongoClient:
    def __init__(self):
        try:
            load_dotenv()
            # print(os.getenv('MONGO_CLIENT'))
            self.client = pymongo.MongoClient(os.getenv('MONGO_CLIENT')) #Mongoclient se thay the bang bien trong .env
            self.db = self.client[os.getenv('TRAFFIC_DB')] #Ten DB se duoc thay bang bien tren db
        except PyMongoError as e:
            print(e)
            
    def createDatabase(self):
        time.sleep(10)
        for coll in self.db.list_collection_names():
            self.db.drop_collection(coll)

        #Mang data #xong ctrl #xong main
        self.createDataCollection()
        self.createImageCollection()
        self.createTextCollection()

        #Mang OSM #xong ctrl chưa có test chưa swagger
        self.createNodeOSMCollection()
        self.createWayOSMCollection()
        self.createRelationOSMCollection()

        #Mang segments #Chưa swagger chưa test #
        self.createSegmentCollection()
        self.createWardCollection()
        self.createCityCollection()
        self.createProvinceCollection()

        #Mang user # xong ctrl #xong main
        self.createUserCollection()
        self.createNotificationCollection()

        #Mang status #xong ctrl chưa test
        # self.createStatusCollection()
        self.createStatusInfoCollection()

        #Nhap OSM, ward
        self.insertProvinceCityWard()
        self.importOSM()
        
    def importOSM(self):
        handler = OSMHandler()
        handler.apply_file(os.getenv('OSMSTORAGE'), locations=True)
        print("Import completed!")
    def createProvinceCollection(self):
        try:
            self.db.create_collection("provinces", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["provinceName"],
                    "properties": {
                        "provinceName": {"bsonType": "string"}
                    }
                }
            })
        except PyMongoError as e:
            print(e)
            
    def createCityCollection(self):
        try:
            self.db.create_collection("cities", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["ProvinceID", "cityName"],
                    "properties": {
                        "ProvinceID": {"bsonType": "objectId"},
                        "cityName": {"bsonType": "string"},
                    }
                }
            })
        except PyMongoError as e:
            print(e)
                   
    def createWardCollection(self):
        try:
            self.db.create_collection("wards", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["CityID", "wardName"],
                    "properties": {
                        "CityID": {"bsonType": "objectId"},
                        "wardName": {"bsonType": "string"},
                    }
                }
            })
        except PyMongoError as e:
            print(e)

    def createStatusInfoCollection(self):
        try:
            self.db.create_collection("statusInfos", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["velocity, statuses"],
                    "properties": {
                        "velocity": {"bsonType": "int"},
                        "statuses": {
                            "bsonType": "object",
                            "required": [
                                'AccidentFlag',
                                'Flooded',
                                'PoliceFlag',
                                'TrafficJamFlag'
                            ],
                            "properties": {
                                "AccidentFlag":{"bsonType": "bool"},
                                "Flooded": {"bsonType": "bool"},
                                "PoliceFlag": {"bsonType": "bool"},
                                "TrafficJamFlag": {"bsonType": "bool"}
                            }
                        }
                    }
                }
            })
        except PyMongoError as e:
            print(e)
            
    def createUserCollection(self):
        try:
            self.db.create_collection("users", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["fullName", "username", "password", "admin"],
                    "properties": {
                        "fullName": {"bsonType": "string"},
                        "phoneNum": {"bsonType": "string"},
                        "email": {"bsonType": "string"},
                        "DoB": {"bsonType": "date"},
                        "status": {"bsonType": "bool"},
                        "loginType": {"bsonType": "string"},
                        "username": {"bsonType": "string"},
                        "password": {"bsonType": "string"},
                        "admin": {"bsonType": "bool"}
                    }
                }
            })
            self.db.users.create_index("username", unique=True)
            self.db.users.create_index("email", unique=True)
        except PyMongoError as e:
            print(e)
            
    def createDataCollection(self):
        try:
            self.db.create_collection("data", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["uploaderID", "type", "uploadTime"],
                    "properties": {
                        "reportID": {"bsonType": "objectId"},
                        "type": {
                            "bsonType": "string",
                            "enum": ["image", "text"]
                        },
                        "InfoID": {"bsonType": "objectId"},
                        "uploadTime": {"bsonType": "date"},
                        "processed": {"bsonType": "bool"},
                        "processed_time": {"bsonType": "date"},
                        "TrainValTest": {"bsonType": "int"},
                        "location": {"bsonType": "string"},
                    }
                }
            })
        except PyMongoError as e:
            print(e)
            
    def createImageCollection(self):
        try:
            self.db.create_collection("images", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["dataID", "source", "length", "contentType", "encoding"],
                    "properties": {
                        "dataID": {"bsonType": "objectId"},
                        "source": {"bsonType": "string"},
                        "length": {"bsonType": "int"},
                        "contentType": {"bsonType": "string"},
                        "encoding": {"bsonType": "string"},
                    }
                }
            })
            self.db.images.create_index("dataID", unique=True)
        except PyMongoError as e:
            print(e)
            
    def createTextCollection(self):
        try:
            self.db.create_collection("texts", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["dataID", "source"],
                    "properties": {
                        "dataID": {"bsonType": "objectId"},
                        "source": {"bsonType": "string"}
                    }
                }
            })
            self.db.texts.create_index("dataID", unique=True)
        except PyMongoError as e:
            print(e)
            
    def createNotificationCollection(self):
        try:
            self.db.create_collection("notifications", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["userID", "type", "content"],
                    "properties": {
                        "userID": {"bsonType": "objectId"},
                        "type": {"bsonType": "string"},
                        "content": {"bsonType": "string"},
                    }
                }
            })
        except PyMongoError as e:
            print(e)
    def createNodeOSMCollection(self):
        try:
            self.db.create_collection("nodes", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["type", "id", "location"],
                    "properties": {
                        "type": {"bsonType": "string"},
                        "id": {"bsonType": ["int","long"]},
                        "location": {
                            "bsonType": "object"
                        },
                        "tags": {"bsonType": "object"},
                        "version": {"bsonType": "int"},
                        "timestamp": {"bsonType": "date"},
                        "changeset": {"bsonType": "int"},
                        "uid": {"bsonType": "int"},
                        "user": {"bsonType": "string"}
                    }
                    
                }
            })
            self.db.nodes.create_index("id", unique=True)
        except PyMongoError as e:
            print(e)
            
    def createSegmentCollection(self):
        try:
            self.db.create_collection("segments", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["way_id","nodes"],
                    "properties": {
                        "type": {"bsonType": "string"},
                        "id": {"bsonType": "string"},
                        "way_id": {"bsonType": "int"},
                        "nodes": {"bsonType": "array"},
                        "tags": {"bsonType": "object"},
                        "version": {"bsonType": "int"},
                        "timestamp": {"bsonType": "date"},
                        "changeset": {"bsonType": "int"},
                        "uid": {"bsonType": "int"},
                        "user": {"bsonType": "string"},
                    }
                }
            })
            self.db.segments.create_index("id", unique=True)
        except PyMongoError as e:
            print(e)
    def createWayOSMCollection(self):
        try:
            self.db.create_collection("ways", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["id","nodes","type"],
                    "properties": {
                        "type": {"bsonType": "string"},
                        "id": {"bsonType": ["int","long"]},
                        "nodes": {"bsonType": "array"},
                        "tags": {"bsonType": "object"},
                        "version": {"bsonType": "int"},
                        "timestamp": {"bsonType": "date"},
                        "changeset": {"bsonType": "int"},
                        "uid": {"bsonType": "int"},
                        "user": {"bsonType": "string"}
                    }
                }
            })
            self.db.ways.create_index("id", unique=True)
        except PyMongoError as e:
            print(e)
            
    def createRelationOSMCollection(self):
        try:
            self.db.create_collection("relations", validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["id","members","tags"],
                    "properties": {
                        "type": {"bsonType": "string"},
                        "id": {"bsonType": ["int","long"]},
                        "members": {"bsonType": "array"},
                        "tags": {"bsonType": "object"},
                        "version": {"bsonType": "int"},
                        "timestamp": {"bsonType": "date"},
                        "changeset": {"bsonType": "int"},
                        "uid": {"bsonType": "int"},
                        "user": {"bsonType": "string"}
                    }
                }
            })
            self.db.relations.create_index("id",unique=True)
        except PyMongoError as e:
            print(e)
            
    def createReportCollection(self):
        self.db.create_collection("reports",validator={
            "$jsonSchema": {
                "bsonType": "object",
                    "required": ["way_id","nodes"],
                    "properties": {
                        "senderID": {"bsonType": "objectId"},
                        "textID": {"bsonType": "objectId"},
                        "imageID": {"bsonType": "objectId"},
                        "eval": {"bsonType": "float"},
                        "qualified": {"bsonType": "bool"}
                    }
            }
        })

    def createRefreshTokenCollection(self):
        self.db.create_collection("refreshTokens",validator={
            "$jsonSchema": {
                "bsonType": "object",
                    "required": ["userID","token"],
                    "properties": {
                        "token": {"bsonType": "string"},
                        "username": {"bsonType": "string"},
                        "expiredAt": {"bsonType": "date"},
                    }
            }
        })

    def insertProvinceCityWard(self):
        provinces_collection = self.db['provinces']
        cities_collection = self.db['cities']
        wards_collection = self.db['wards']
        province = {"provinceName": "Thành phố Hồ Chí Minh"}
        province_result = provinces_collection.insert_one(province)
        province_id = province_result.inserted_id

        # List of districts and wards based on 2025 data
        districts = [
            {"cityName": "Quận 1"},
            {"cityName": "Quận 3"},
            {"cityName": "Quận 4"},
            {"cityName": "Quận 5"},
            {"cityName": "Quận 6"},
            {"cityName": "Quận 7"},
            {"cityName": "Quận 8"},
            {"cityName": "Quận 10"},
            {"cityName": "Quận 11"},
            {"cityName": "Quận 12"},
            {"cityName": "Bình Thạnh"},
            {"cityName": "Gò Vấp"},
            {"cityName": "Phú Nhuận"},
            {"cityName": "Tân Bình"},
            {"cityName": "Tân Phú"},
            {"cityName": "Bình Tân"},
            {"cityName": "Thành phố Thủ Đức"},
            {"cityName": "Huyện Bình Chánh"},
            {"cityName": "Huyện Cần Giờ"},
            {"cityName": "Huyện Củ Chi"},
            {"cityName": "Huyện Hóc Môn"},
            {"cityName": "Huyện Nhà Bè"}
        ]

        # Insert Districts/Cities
        cities = [{"ProvinceID": province_id, "cityName": d["cityName"]} for d in districts]
        city_results = cities_collection.insert_many(cities)
        city_ids = city_results.inserted_ids

        # Map of wards for each district (simplified example based on available data)
        wards_data = {
            city_ids[0]: ["Bến Thành", "Bến Nghé", "Đa Kao", "Nguyễn Cư Trinh", "Nguyễn Thái Bình", "Tân Định", "Cô Giang", "Cầu Ông Lãnh", "Phạm Ngũ Lão", "Cầu Kho"],  # Quận 1
            city_ids[1]: ["Bàn Cơ", "Xuân Hòa", "Nhiêu Lộc"],  # Quận 3 (post-merge)
            city_ids[2]: ["Xóm Chiếu", "Khánh Hội"],  # Quận 4 (post-merge)
            city_ids[3]: ["", "", "", "", ""],  # Quận 5 (placeholder)
            city_ids[4]: ["", "", "", "", ""],  # Quận 6 (placeholder)
            city_ids[5]: ["Bình Thuận", "Phú Mỹ", "Phú Thuận", "Tân Hưng", "Tân Kiểng", "Tân Phong", "Tân Phú", "Tân Quý", "Tân Thuận Tây", "Tân Thuận Đông"],  # Quận 7
            city_ids[6]: ["Bình Đông", "Phú Định"],  # Quận 8 (post-merge)
            city_ids[7]: ["", "", "", "", ""],  # Quận 10 (placeholder)
            city_ids[8]: ["", "", "", "", ""],  # Quận 11 (placeholder)
            city_ids[9]: ["An Phú Đông", "Đông Hưng Thuận", "Hiệp Thành", "Tân Chánh Hiệp", "Tân Hưng Thuận", "Tân Thới Hiệp", "Tân Thới Nhất", "Thạnh Lộc", "Thạnh Xuân", "Thới An", "Trung Mỹ Tây"],  # Quận 12
            city_ids[10]: ["", "", "", "", ""],  # Bình Thạnh (placeholder)
            city_ids[11]: ["An Nhơn", "Gò Vấp"],  # Gò Vấp (post-merge)
            city_ids[12]: ["", "", "", "", ""],  # Phú Nhuận (placeholder)
            city_ids[13]: ["", "", "", "", ""],  # Tân Bình (placeholder)
            city_ids[14]: ["", "", "", "", ""],  # Tân Phú (placeholder)
            city_ids[15]: ["Bình Hưng Hòa", "Bình Trị Đông", "An Lạc", "Tân Tạo"],  # Bình Tân (post-merge)
            city_ids[16]: ["An Khánh", "An Lợi Đông", "An Phú", "Bình Chiểu", "Bình Thọ", "Bình Trưng Đông", "Bình Trưng Tây", "Cát Lái", "Hiệp Bình Chánh", "Hiệp Bình Phước", "Hiệp Phú", "Linh Chiểu", "Linh Đông", "Linh Tây", "Linh Trung", "Linh Xuân", "Long Bình", "Long Phước", "Long Thạnh Mỹ", "Long Trường", "Phú Hữu", "Phước Bình", "Phước Long A", "Phước Long B", "Tam Bình", "Tam Phú", "Tăng Nhơn Phú A", "Tăng Nhơn Phú B", "Tân Phú", "Thảo Điền", "Thạnh Mỹ Lợi", "Thủ Thiêm", "Trường Thạnh", "Trường Thọ"],  # TP Thủ Đức
            city_ids[17]: ["Bình Chánh", "Bình Hưng", "Bình Lợi", "Đa Phước", "Hưng Long", "Lê Minh Xuân", "Phong Phú", "Tân Kiên", "Tân Nhựt", "Tân Quý Tây", "Vĩnh Lộc A", "Vĩnh Lộc B"],  # Huyện Bình Chánh (post-merge)
            city_ids[18]: ["An Thới Đông", "Bình Khánh", "Long Hòa", "Lý Nhơn", "Tam Thôn Hiệp", "Thạnh An"],  # Huyện Cần Giờ
            city_ids[19]: ["Phú Mỹ Hưng", "Tân An Hội", "Tân Phú Trung", "Tân Thạnh Đông", "Tân Thạnh Tây", "Thái Mỹ", "Phước Thạnh", "Phước Vĩnh An", "Trung An", "Trung Lập Hạ", "Trung Lập Thượng", "An Phú", "Nhuận Đức"],  # Huyện Củ Chi
            city_ids[20]: ["Bà Điểm", "Đông Thạnh", "Hóc Môn", "Tân Hiệp", "Tân Xuân", "Thới Tam Thôn", "Xuân Thới Đông", "Xuân Thới Sơn"],  # Huyện Hóc Môn
            city_ids[21]: ["Hiệp Phước", "Nhà Bè", "Phú Xuân"]  # Huyện Nhà Bè (post-merge)
        }

        # Insert Wards
        wards = []
        for city_id, ward_names in wards_data.items():
            for ward_name in ward_names:
                if ward_name:  # Skip empty placeholders
                    wards.append({"CityID": city_id, "wardName": ward_name})
        if wards:
            wards_collection.insert_many(wards)
class OSMHandler(o.SimpleHandler):
    def __init__(self):
        super(OSMHandler, self).__init__()
        self.trafficClient = TrafficMongoClient()
        self.nodes = self.trafficClient.db["nodes"]
        self.ways = self.trafficClient.db["ways"]
        self.segments = self.trafficClient.db["segments"]
        self.relations = self.trafficClient.db["relations"]
        
    def node(self, n):
        doc = {
            "type": "node",
            "id": n.id,
            "location": {
                "type": "Point",
                "coordinates": [n.location.lon, n.location.lat]
            },
            "tags": dict(n.tags),
            "version": n.version,
            "timestamp": datetime.fromisoformat(n.timestamp.isoformat()),
            "changeset": n.changeset,
            "uid": n.uid,
            "user": n.user
        }
        try:
            self.nodes.insert_one(doc)
            print(f'node {n.id}')
        except PyMongoError as e:
            print(e)
            sys.exit(1)
            
    
    def way(self, w):
        # Lưu Way
        doc = {
            "type": "way",
            "id": w.id,
            "nodes": [n.ref for n in w.nodes],
            "tags": dict(w.tags),
            "version": w.version,
            "timestamp": datetime.fromisoformat(w.timestamp.isoformat()),
            "changeset": w.changeset,
            "uid": w.uid,
            "user": w.user
        }
        try:
            self.ways.insert_one(doc)
            print(f'way {w.id}')
        except PyMongoError as e:
            print(e)
            sys.exit(1)
            
        
        # Tạo Segments từ Way
        node_refs = [n.ref for n in w.nodes]
        tags = dict(w.tags)
        
        # Tạo segments với 2 hoặc 3 nodes
        for i in range(len(node_refs) - 1):  # Duyệt qua các node để tạo segment
            if i + 2 <= len(node_refs):  # Đảm bảo không vượt quá số node
                segment_nodes = node_refs[i:i + 1]
                segment_doc = {
                    "type": "segment",
                    "id": f"{w.id}_{i}",  # ID duy nhất: way_id_index_size
                    "way_id": w.id,
                    "nodes": segment_nodes,
                    "tags": tags,
                    "version": w.version,
                    "timestamp": datetime.fromisoformat(w.timestamp.isoformat()),
                    "changeset": w.changeset,
                    "uid": w.uid,
                    "user": w.user
                }
                try:
                    self.segments.insert_one(segment_doc)
                except PyMongoError as e:
                    print(e)
                    sys.exit(1)
                    
    

    def relation(self, r):
        members = [{
            "type": m.type,
            "ref": m.ref,
            "role": m.role
        } for m in r.members]
        
        doc = {
            "type": "relation",
            "id": r.id,
            "members": members,
            "tags": dict(r.tags),
            "version": r.version,
            "timestamp": datetime.fromisoformat(r.timestamp.isoformat()),
            "changeset": r.changeset,
            "uid": r.uid,
            "user": r.user
        }
        try:
            self.relations.insert_one(doc)
            print(f'relation {r.id}')
        except PyMongoError as e:
            print(e)
            sys.exit(1)
    
    
            

# a = TrafficMongoClient()
# a.createDatabase()