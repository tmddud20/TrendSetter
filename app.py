import random

from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from bson.json_util import dumps

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('3.36.70.96', 27017, username="test", password="test")
db = client


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.clothes.users.find_one({"username": payload["id"]})

        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/get_rec', methods=['POST'])
def get_rec():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        user_color_info = db.color_info[payload["id"]].find_one({"username": payload["id"]})
        user_kind_info = db.kind_info[payload["id"]].find_one({"username": payload["id"]})
        user_material_info = db.material_info[payload["id"]].find_one({"username": payload["id"]})
        user_price_info = db.price_info[payload["id"]].find_one({"username": payload["id"]})

        color_numbers = [user_color_info['view_red'], user_color_info['view_orange'], user_color_info['view_yellow'],
                         user_color_info['view_green'],
                         user_color_info['view_blue'], user_color_info['view_white'], user_color_info['view_black'],
                         user_color_info['view_gray']]
        color_name = ['red', 'orange', 'yellow', 'green', 'blue', 'white', 'black', 'gray']

        max_value = max(color_numbers)
        if max_value != 0:
            max_color = color_name[color_numbers.index(max_value)]
        color_numbers.remove(max_value)
        color_name.remove(max_color)
        max_value = max(color_numbers)
        second_color = color_name[color_numbers.index(max_value)]
        print(max_color, second_color)

        kind_numbers = [user_kind_info['view_hood'], user_kind_info['view_knit'],
                        user_kind_info['view_short_tshirt'],
                        user_kind_info['view_mtm'], user_kind_info['view_shirt'], user_kind_info['view_padding'],
                        user_kind_info['view_coat'], user_kind_info['view_vest']]
        kind_name = ['hood', 'knit', 'short_tshirt', 'mtm', 'shirt', 'padding', 'coat', 'vest']

        max_value = max(kind_numbers)
        max_kind = kind_name[kind_numbers.index(max_value)]
        kind_numbers.remove(max_value)
        kind_name.remove(max_kind)
        max_value = max(kind_numbers)
        second_kind = kind_name[kind_numbers.index(max_value)]
        print(max_kind, second_kind)

        material_numbers = [user_material_info['view_cotton'], user_material_info['view_poli'],
                            user_material_info['view_etc']]
        material_name = [' 면', ' 폴리에스테르', ' 기타']

        max_value = max(material_numbers)
        max_material = material_name[material_numbers.index(max_value)]
        material_numbers.remove(max_value)
        material_name.remove(max_material)
        max_value = max(material_numbers)
        second_material = material_name[material_numbers.index(max_value)]
        print(max_material, second_material)

        price_numbers = [user_price_info['view_0to3'], user_price_info['view_3to6'], user_price_info['view_6to9'],
                         user_price_info['view_9to12'], user_price_info['view_12to15'], user_price_info['view_15to']]
        price_name = ['0to3', '3to6', '6to9', '9to12', '12to15', '15to']

        max_value = max(price_numbers)
        max_price = price_name[price_numbers.index(max_value)]
        price_numbers.remove(max_value)
        price_name.remove(max_price)
        max_value = max(price_numbers)
        second_price = price_name[price_numbers.index(max_value)]
        print(max_price, second_price)

        max_max = list(db.clothes.products.find({'color': max_color, 'kind': max_kind})
                       .skip(random.randrange(1, 5)).limit(2))
        max_sec = list(db.clothes.products.find({'color': max_color, 'kind': second_kind})
                       .skip(random.randrange(1, 5)).limit(1))
        sec_max = list(db.clothes.products.find({'color': second_color, 'kind': max_kind})
                       .skip(random.randrange(1, 5)).limit(1))
        sec_sec = list(db.clothes.products.find({'color': second_color, 'kind': second_kind})
                       .skip(random.randrange(1, 5)).limit(1))

        max_max3 = list(db.clothes.products.find({'color': max_color, 'material': max_material})
                        .skip(random.randrange(1, 5)).limit(1))

        return jsonify({'result': 'success', 'max_max': dumps(max_max), 'max_sec': dumps(max_sec),
                        'sec_max': dumps(sec_max), 'sec_sec': dumps(sec_sec), 'max_max3': dumps(max_max3)})
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/detail/<item>')
def detail(item):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        items = list(db.clothes.products.find({'kind': item}, {'_id': False}))

        user_info = db.clothes.users.find_one({"username": payload["id"]})
        return render_template('detail.html', user_info=user_info, items=items)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/detail2/<item2>')
def detail2(item2):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        detailed_item = db.clothes.products.find_one({'name': item2}, {'_id': False})

        # print(detailed_item['name'], detailed_item['color'], detailed_item['price'])
        user_info = db.clothes.users.find_one({"username": payload["id"]})
        return render_template('detail2.html', user_info=user_info, detailed_item=detailed_item)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/viewd', methods=['POST'])
def viewd():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.clothes.users.find_one({"username": payload["id"]})

        item_color = "view_" + request.form["item_color"]
        item_kind = "view_" + request.form["item_kind"]
        item_price = request.form["item_price"]
        item_price = item_price.replace("원", "")
        item_price = item_price.replace(",", "")
        item_material = request.form["item_material"]

        if int(item_price) < 30000:
            item_price = "view_0to3"
        elif int(item_price) < 60000:
            item_price = "view_3to6"
        elif int(item_price) < 90000:
            item_price = "view_6to9"
        elif int(item_price) < 120000:
            item_price = "view_9to12"
        elif int(item_price) < 150000:
            item_price = "view_12to15"
        else:
            item_price = "view_15to"

        if "폴리에스테르" in item_material:
            item_material = "view_poli"
        elif "면" in item_material:
            item_material = "view_cotton"
        else:
            item_material = "view_etc"

        view_item_color = db.color_info[payload["id"]].find_one({"username": payload["id"]})
        view_item_kind = db.kind_info[payload["id"]].find_one({"username": payload["id"]})
        view_item_price = db.price_info[payload["id"]].find_one({"username": payload["id"]})
        view_item_material = db.material_info[payload["id"]].find_one({"username": payload["id"]})

        color_plus1 = view_item_color[item_color] + 1
        kind_plus1 = view_item_kind[item_kind] + 1
        price_plus1 = view_item_price[item_price] + 1
        material_plus1 = view_item_material[item_material] + 1

        db.color_info[payload["id"]].update_one({'username': payload["id"]}, {'$set': {item_color: color_plus1}})
        db.kind_info[payload["id"]].update_one({'username': payload["id"]}, {'$set': {item_kind: kind_plus1}})
        db.price_info[payload["id"]].update_one({'username': payload["id"]}, {'$set': {item_price: price_plus1}})
        db.material_info[payload["id"]].update_one({'username': payload["id"]}, {'$set': {item_material: material_plus1}})

        return jsonify({"result": "success"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/buy', methods=['POST'])
def buy():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.clothes.users.find_one({"username": payload["id"]})

        item_color = "buy_" + request.form["item_color"]
        item_kind = "buy_" + request.form["item_kind"]
        item_price = request.form["item_price"]
        item_price = item_price.replace("원", "")
        item_price = item_price.replace(",", "")
        item_material = request.form["item_material"]

        if int(item_price) < 30000:
            item_price = "buy_0to3"
        elif int(item_price) < 60000:
            item_price = "buy_3to6"
        elif int(item_price) < 90000:
            item_price = "buy_6to9"
        elif int(item_price) < 120000:
            item_price = "buy_9to12"
        elif int(item_price) < 150000:
            item_price = "buy_12to15"
        else:
            item_price = "buy_15to"

        if "폴리에스테르" in item_material:
            item_material = "buy_poli"
        elif "면" in item_material:
            item_material = "buy_cotton"
        else:
            item_material = "buy_etc"

        view_item_color = db.color_info[payload["id"]].find_one({"username": payload["id"]})
        view_item_kind = db.kind_info[payload["id"]].find_one({"username": payload["id"]})
        view_item_price = db.price_info[payload["id"]].find_one({"username": payload["id"]})
        view_item_material = db.material_info[payload["id"]].find_one({"username": payload["id"]})

        color_plus1 = view_item_color[item_color] + 1
        kind_plus1 = view_item_kind[item_kind] + 1
        price_plus1 = view_item_price[item_price] + 1
        material_plus1 = view_item_material[item_material] + 1

        db.color_info[payload["id"]].update_one({'username': payload["id"]}, {'$set': {item_color: color_plus1}})
        db.kind_info[payload["id"]].update_one({'username': payload["id"]}, {'$set': {item_kind: kind_plus1}})
        db.price_info[payload["id"]].update_one({'username': payload["id"]}, {'$set': {item_price: price_plus1}})
        db.material_info[payload["id"]].update_one({'username': payload["id"]}, {'$set': {item_material: material_plus1}})

        return jsonify({"result": "success", 'msg': '구매 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.clothes.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.clothes.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_placeholder.png",
        "profile_info": "",
    }
    db.clothes.users.insert_one(doc)

    doc = {
        "username": username_receive,
        "view_red": 0,
        "view_orange": 0,
        "view_yellow": 0,
        "view_green": 0,
        "view_blue": 0,
        "view_white": 0,
        "view_black": 0,
        "view_gray": 0,

        "buy_red": 0,
        "buy_orange": 0,
        "buy_yellow": 0,
        "buy_green": 0,
        "buy_blue": 0,
        "buy_white": 0,
        "buy_black": 0,
        "buy_gray": 0,
    }
    db.color_info[username_receive].insert_one(doc)

    doc = {
        "username": username_receive,
        "view_hood": 0,
        "view_knit": 0,
        "view_short_tshirt": 0,
        "view_mtm": 0,
        "view_shirt": 0,
        "view_padding": 0,
        "view_coat": 0,
        "view_vest": 0,

        "buy_hood": 0,
        "buy_knit": 0,
        "buy_short_tshirt": 0,
        "buy_mtm": 0,
        "buy_shirt": 0,
        "buy_padding": 0,
        "buy_coat": 0,
        "buy_vest": 0
    }
    db.kind_info[username_receive].insert_one(doc)

    doc = {
        "username": username_receive,
        "view_0to3": 0,
        "view_3to6": 0,
        "view_6to9": 0,
        "view_9to12": 0,
        "view_12to15": 0,
        "view_15to": 0,

        "buy_0to3": 0,
        "buy_3to6": 0,
        "buy_6to9": 0,
        "buy_9to12": 0,
        "buy_12to15": 0,
        "buy_15to": 0
    }
    db.price_info[username_receive].insert_one(doc)

    doc = {
        "username": username_receive,
        "view_cotton": 0,
        "view_poli": 0,
        "view_etc": 0,

        "buy_cotton": 0,
        "buy_poli": 0,
        "buy_etc": 0
    }
    db.material_info[username_receive].insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.clothes.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.clothes.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route("/get_cur_view", methods=['POST'])
def get_cur_view():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        item_color_receive = request.form["item_color_give"]
        item_kind_receive = request.form["item_kind_give"]

        same_color_kind = list(db.clothes.products.find({'color': item_color_receive, 'kind': item_kind_receive}))
        same_color_kind2 = list(db.clothes.products.find({'color': item_color_receive,
                                                         'kind': item_kind_receive}).skip(random.randrange(1, len(same_color_kind))).limit(2))

        same_color = list(db.clothes.products.find({'color': item_color_receive}))
        same_color2 = list(db.clothes.products.find({'color': item_color_receive}).skip(random.randrange(1, len(same_color))).limit(1))

        same_kind = list(db.clothes.products.find({'kind': item_kind_receive}))
        same_kind2 = list(db.clothes.products.find({'kind': item_kind_receive}).skip(random.randrange(1, len(same_kind))).limit(1))
        return jsonify({"same_color_kind": dumps(same_color_kind2), "same_color": dumps(same_color2), "same_kind": dumps(same_kind2)})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
