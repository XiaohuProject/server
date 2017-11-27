import json
import uuid
from datetime import datetime

from flask import Flask, request
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
api_key = 'acq9Rj5Lyej'
Base = declarative_base()


@app.route("/hello_world")
def hello():
    user = request.args.get("user")
    return "user {} is visited, return random id: {}".format(user, uuid.uuid1())


@app.route('/bsr/profile/set')
def set_profile():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    name = request.args.get("name")
    cid = request.args.get("cid")
    wid = request.args.get("wid")  # 呼号
    enter_time = datetime.strptime(request.args.get("enter_time"), "%Y%m%d")
    gender = request.args.get("gender")

    with SessionWrapper() as sess:
        profile = BSRProfile(cid=cid, wid=wid, enter_time=enter_time.strftime("%Y-%m-%d %H:%M:%S"),
                             gender=gender, name=name)
        sess.add(profile)
        sess.commit()
        sess.flush()
        uid = profile.uid

    ret = {'code': 200, 'uid': uid}
    return json.dumps(ret)


@app.route('/bsr/profile/get')
def get_profile():
    user_id = request.args.get("user_id")


@app.route('/bsr/footprint/set')
def set_footprint():
    pass


@app.route('/bsr/footprint/get')
def get_footprint():
    user_id = request.args.get("user_id")
    pass


@app.route('/bsr/exam/set')
def set_exam():
    pass


@app.route('/bsr/exam/get')
def get_exam():
    user_id = request.args.get("user_id")
    pass


class BSRProfile(Base):
    __tablename__ = 'profile'

    uid = Column(Integer, primary_key=True)
    name = Column(String)
    cid = Column(String)
    wid = Column(String)
    enter_time = Column(DateTime)
    gender = Column(String)


class SessionWrapper:
    def __init__(self):
        engine = create_engine("mysql+pymysql://root:Mideep2017#@localhost/bsr?charset=utf8",
                               encoding='utf-8', echo=True)
        session_maker = sessionmaker(bind=engine)
        self.session = session_maker()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()


if __name__ == "__main__":
    app.run(port=7777)
