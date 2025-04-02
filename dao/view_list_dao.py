import pymysql
import sys
sys.path.append(".")
from vo.view_list_vo import ViewlistVO

class ViewlistDAO:
    def __init__(self):
        self.conn = pymysql.connect(
            host="158.247.211.92",
            port=3306,
            user="milk",
            password="0621",
            database="hotplace"
        )
        self.cursor = self.conn.cursor()
    
    #추가
    def insert_view_list(self, id, sno):
        sql = "insert into view_list(id, sno)values(%s, %s)"
        self.cursor.execute(sql, (id, sno))
        self.conn.commit()

    #조회
    def select_view_list(self, id):
        sql = "select * from view_list order by 'no' desc limit 5 where id=%s"
        self.cursor.execute(sql, (id))
        result = self.cursor.fetchall()
        view_lists = []
        for view_list in result:
            no, id, sno = view_list
            vo = ViewlistVO(no, id, sno)
            view_lists.append(vo)
        return view_lists
            
        