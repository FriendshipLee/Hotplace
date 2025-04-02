import pymysql
import sys
sys.path.append(".")
from vo.place_vo import PlaceVO

class PlaceDAO:
    def __init__(self):
        self.conn = pymysql.connect(
            host="158.247.211.92",
            port=3306,
            user="milk",
            password="0621",
            database="hotplace"
        )
        self.cursor = self.conn.cursor()
        print("쿼리 객체 생성")

    #검색 조회
    def search_places(self, q):
        sql = "select * from place where title like %s or sigungu like %s"
        self.cursor.execute(sql, (q, q))
        result = self.cursor.fetchall()
        places = []
        for place in result:
            contentid, overview, homepage, addr1, cat1, cat2, cat3, firstimage, mapx, mapy, title, sigungu = result
            vo = PlaceVO(contentid, overview, homepage, addr1, cat1, cat2, cat3, firstimage, mapx, mapy, title, sigungu)
            places.append(vo)
        return places

    #목록 조회
    def get_all_place(self):
        sql = "select * from place limit 5"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        places = []
        for place in result:
            contentid, overview, homepage, addr1, cat1, cat2, cat3, firstimage, mapx, mapy, title, sigungu = place
            vo = PlaceVO(contentid, overview, homepage, addr1, cat1, cat2, cat3, firstimage, mapx, mapy, title, sigungu)
            places.append(vo)
        return places
    
    #단건 조회(post)
    def get_one_place(self, contentid):
        sql = "select * from place where contentid = %s"
        self.cursor.execute(sql, (contentid))
        result = self.cursor.fetchone()
        if result:
            contentid, overview, homepage, addr1, cat1, cat2, cat3, firstimage, mapx, mapy, title, sigungu = result
            return PlaceVO(contentid, overview, homepage, addr1, cat1, cat2, cat3, firstimage, mapx, mapy, title, sigungu)
        else:
            return None
