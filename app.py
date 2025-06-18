from flask import Flask, redirect, render_template, request, session, jsonify
from dao.user_dao import UserDAO
from dao.place_dao import PlaceDAO
from vo.place_vo import PlaceVO
from dao.view_list_dao import ViewlistDAO
from dao.favorites_dao import FavoritesDAO
from dao.similar_dao import SimilarDAO
from dao.review_dao import ReviewDAO
from util.mobility import mobility
import json

app = Flask(__name__)
app.secret_key = "keyy"

@app.route("/")
def home():
    dao=PlaceDAO()
    vo = dao.popularity_places()
    return render_template("home.html", items=vo)     

@app.route("/join", methods=["POST"])
def join():
    id = request.form.get("id")
    pw = request.form.get("pw")
    name = request.form.get("name")
    email = request.form.get("email")
    dao = UserDAO()
    dao.join(id, pw, name, email)
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    id = request.form.get("id")
    pw = request.form.get("pw")
    dao = UserDAO()
    result = dao.login(id, pw)
    if result:
        session["id"] = id
    return redirect("/")

@app.route("/mypage")
def mypage():
    if "id" in session:
        #session 딕셔너리 키에 hong이 있으면
        dao = UserDAO()
        id = session.get("id")
        vo = dao.get_one_user(id)
        
        vdao = ViewlistDAO()
        list = vdao.select_view_list(id)
        
        return render_template("mypage.html", data=vo, a="data", lists=list)
    else:
        return render_template("home.html")

@app.route("/logout")
def logout():
     session.pop("id", None)
     return render_template("home.html")

@app.route("/board", methods=["GET"])
def board():
    dao = PlaceDAO()
    search = request.args.get("search")
    if search is None:
        search == ""
    id = session.get("id")
    cnt = dao.get_count_search(search)
    result = dao.search_places(id, search)
    return render_template("board.html", items=result, count=cnt[0], search=search)

@app.route("/board_plus", methods=["GET"])
def board_plus():
    id = session.get("id")
    page = request.args.get("page")
    search = request.args.get("search")

    dao = PlaceDAO()
    result = dao.get_all_place(id, page=page, search=search)
    
    result_dict = []
    for vo in result:
        result_dict.append(vo.to_dict())
        #PlaceVO 객체를 to_dict()를 통해 JSON으로 전송
    return jsonify(result=result_dict)

@app.route("/region", methods=["GET"])
def region():
    dao = PlaceDAO()
    id = session.get("id")
    regions = request.args.getlist("region")
    val = ", ".join(list(map(lambda x : f"\'{x}\'", regions)))
    vo = dao.get_all_place(id, val)
    cnt = dao.get_count_region(val)
    return render_template("region.html", items=vo, regions=regions, count=cnt[0])

@app.route("/region_plus", methods=["GET"])
def region_plus():
    id = session.get("id")
    page = request.args.get("page")
    regions = request.args.getlist("region")
    
    if not regions:
        regions = []

    val = ", ".join(list(map(lambda x : f"\'{x}\'", regions)))
    print(val)
    dao = PlaceDAO()
    result = dao.get_all_place(id, val, page)
    
    result_dict = []
    for vo in result:
        result_dict.append(vo.to_dict())
        #PlaceVO 객체를 to_dict()를 통해 JSON으로 전송
    return jsonify(result=result_dict)

@app.route("/theme", methods=["GET"])
def theme():
    dao = PlaceDAO()
    id = session.get("id")
    cats = request.args.getlist("cat")
    val = ", ".join(list(map(lambda x : f"\'{x}\'", cats)))
    vo = dao.get_theme_place(id, val)
    cnt = dao.get_count_theme(val)
    return render_template("theme.html", items=vo, cats=cats, count=cnt[0])

@app.route("/cat_plus", methods=["GET"])
def cat_plus():
    id = session.get("id")
    page = request.args.get("page")
    cats = request.args.getlist("cat")
    
    if not cats:
        cats = []

    val = ", ".join(list(map(lambda x : f"\'{x}\'", cats)))
    dao = PlaceDAO()
    result = dao.get_theme_place(id, val, page)
    
    result_dict = []
    for vo in result:
        result_dict.append(vo.to_dict())
        #PlaceVO 객체를 to_dict()를 통해 JSON으로 전송
    return jsonify(result=result_dict)

@app.route("/post/<int:contentid>")
def post(contentid):
    
    #로그인 했으면 최근본 관광지 테이블에 인서트
    id = session.get("id")
    if id:
        vdao = ViewlistDAO()
        vo = vdao.insert_view_list(id, contentid)
    else:
        pass
    
    pdao = PlaceDAO()
    vo = pdao.get_one_place(contentid)
    
    sdao = SimilarDAO()
    svo = sdao.select_similar(contentid)
    
    rdao = ReviewDAO()
    rvo = rdao.select_review(contentid)
    print(rvo)

    if vo or svo or rvo:
        return render_template("post.html", data=vo, similars=svo, reviews=rvo)
    return redirect("/region")

@app.route("/review/<int:contentid>")
def review(contentid):
    dao = ReviewDAO()
    vo = dao.select_review(contentid)
    return render_template("review.html", reviews=vo)

@app.route("/favorite", methods=["GET"])
def favorite():
    id = session.get("id")
    dao = FavoritesDAO()
    vo = dao.selecte_favorite(id)
    d = list(map(lambda x: str(x.contentid), vo))
    results = dao.random(d)
    return render_template("favorite.html", items=vo, results=results)

@app.route("/favorite_data", methods=["POST"])
def favorite_data():
    dao = FavoritesDAO()
    chInt = request.form.get("chInt")
    contentid = request.form.get("contentid")
    id = session["id"]
    print(contentid)
    print(chInt)
    if chInt == "1":
        dao.insert_favorite(id, contentid)
    else:
        dao.delete_favorite(id, contentid)
    response = jsonify(result=True)
    return response

@app.route("/course", methods=["GET"])
def course():
    
    # return redirect("/course?region=<region>&cat=<cat>", items=vo)
    return render_template("course.html")

@app.route("/course_recommend", methods=["POST"])
def course_recommend():
    region = request.form.get("region")
    cats = request.form.getlist("cat")
    val = ", ".join(list(map(lambda x : f"\'{x}\'", cats)))

    dao = PlaceDAO()
    vo = dao.get_course_place(region, val)
    #기준 관광지 3개 조회
    
    for i, data in enumerate(vo):
        #기준 관광지 3개 만큼 조회  
        sdao = PlaceDAO()
        svo = sdao.path(data.contentid)
        print(svo)
        #유사 관광지 3개 조회 (data.contentid는 현재 기준 관광지의 contentid)
        vo[i].place_vo = svo
        #기준 관광지 10개중 0번인덱스 안에 place_vo에 유사 관광지 리스트 대입
        #꺼내서 쓸때에는 vo.place_vo.contentid -> 유사 관광지의 contentid
    data = mobility(vo)
    #print(data)
    return render_template("course_recommend.html", items=vo, route=data)

#app.run(debug=True, host="0.0.0.0")