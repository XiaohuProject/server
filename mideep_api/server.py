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


@app.route('/bsr/profile/add')
def add_profile():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    name = request.args.get("name")
    openid = request.args.get("openid", "")
    icon = request.args.get("icon", "")
    wid = request.args.get("wid", "")  # 呼号
    create_time = datetime.strptime(request.args.get("create_time"), "%Y%m%d")
    gender = request.args.get("gender", "")

    with SessionWrapper() as sess:
        profile = BSRProfile(openid=openid, wid=wid, icon=icon, create_time=create_time.strftime("%Y-%m-%d %H:%M:%S"),
                             gender=gender, name=name)
        sess.add(profile)
        sess.commit()
        sess.flush()
        uid = profile.uid

    ret = {'code': 200, 'uid': uid}
    return json.dumps(ret)


@app.route('/bsr/profile/update')
def update_profile():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    uid = request.args.get("uid")
    openid = request.args.get("openid", None)
    name = request.args.get("name", None)
    icon = request.args.get("icon", None)
    wid = request.args.get("wid", None)  # 呼号
    create_time = request.args.get("create_time", None)
    gender = request.args.get("gender", None)

    with SessionWrapper() as sess:
        profile = sess.query(BSRProfile).get(uid)
        if profile is None:
            ret = {'code': 401, 'message': 'invalid uid'}
            return json.dumps(ret)

        if openid:
            profile.openid = openid
        if name:
            profile.name = name
        if icon:
            profile.icon = icon
        if wid:
            profile.wid = wid
        if create_time:
            create_time = datetime.strptime(request.args.get("create_time"), "%Y%m%d")
            profile.create_time = create_time
        if gender:
            profile.gender = gender
        sess.commit()
        sess.flush()

    ret = {'code': 200}
    return json.dumps(ret)


@app.route("/bsr/profile/openid/uid")
def get_uid_by_openid():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    openid = request.args.get("openid")
    with SessionWrapper() as sess:
        profile = sess.query(BSRProfile).filter_by(openid=openid).first()
        uid = -1
        if profile is not None:
            uid = profile.uid
        ret = {'code': 200, 'uid': uid}
        return json.dumps(ret)


@app.route("/bsr/profile/name/uid")
def get_uid_by_name():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    name = request.args.get("name")
    with SessionWrapper() as sess:
        profile = sess.query(BSRProfile).filter_by(name=name).first()
        uid = -1
        if profile is not None:
            uid = profile.uid
        ret = {'code': 200, 'uid': uid}
        return json.dumps(ret)


@app.route('/bsr/profile/get')
def get_profile():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    uid = request.args.get("uid")
    with SessionWrapper() as sess:
        profile = sess.query(BSRProfile).get(uid)
        if not profile:
            ret = {'code': 400, 'message': 'invalid uid'}
            return json.dumps(ret)

        ret = {
            'code': 200,
            'profile': {
                'name': profile.name,
                'openid': profile.openid,
                'icon': profile.icon,
                'wid': profile.wid,
                'create_time': profile.create_time.strftime("%Y%m%d"),
                'gender': profile.gender
            }
        }
        return json.dumps(ret)


@app.route('/bsr/profiles/get')
def get_profiles():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    with SessionWrapper() as sess:
        profiles = sess.query(BSRProfile).all()

        ret_profiles = []
        for profile in profiles:
            ret_profiles.append({
                'uid': profile.uid,
                'name': profile.name,
                'openid': profile.openid,
                'icon': profile.icon,
                'wid': profile.wid,
                'create_time': profile.create_time.strftime("%Y%m%d"),
                'gender': profile.gender
            })

        ret = {
            'code': 200,
            'profiles': ret_profiles
        }
        return json.dumps(ret)


@app.route('/bsr/footprint/set')
def set_footprint():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    uid = request.args.get("uid")
    create_time = datetime.strptime(request.args.get("create_time"), "%Y%m%d")
    description = request.args.get("description")
    fp_type = request.args.get("type")
    duration = request.args.get("duration")

    with SessionWrapper() as sess:
        footprint = BSRFootprint(uid=uid, description=description, type=fp_type, duration=duration,
                                 create_time=create_time.strftime("%Y-%m-%d %H:%M:%S"))
        sess.add(footprint)
        sess.commit()
        sess.flush()
        ret = {'code': 200}
        return json.dumps(ret)


@app.route('/bsr/footprint/get')
def get_footprint():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    uid = request.args.get("uid")
    with SessionWrapper() as sess:
        footprints = sess.query(BSRFootprint).filter_by(uid=uid)

        ret_footprints = []
        for footprint in footprints:
            ret_footprints.append({
                'create_time': footprint.create_time.strftime("%Y%m%d"),
                'description': footprint.description,
                'type': footprint.type,
                'duration': footprint.duration
            })

        ret = {
            'code': 200,
            'footprints': ret_footprints
        }
        return json.dumps(ret)


@app.route('/bsr/exam/set')
def set_exam():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    uid = request.args.get("uid")
    create_time = datetime.strptime(request.args.get("create_time"), "%Y%m%d")
    type_a = request.args.get("type_a")
    type_b = request.args.get("type_b")
    number = request.args.get("number")
    result = request.args.get("result")
    mister = request.args.get("mister")

    with SessionWrapper() as sess:
        exam = BSRExam(uid=uid, type_a=type_a, type_b=type_b, number=number, result=result, mister=mister,
                       create_time=create_time.strftime("%Y-%m-%d %H:%M:%S"))
        sess.add(exam)
        sess.commit()
        sess.flush()
        ret = {'code': 200}
        return json.dumps(ret)


@app.route('/bsr/exam/get')
def get_exam():
    ak = request.args.get("ak")
    if ak != api_key:
        ret = {'code': 401, 'message': 'invalid api key'}
        return json.dumps(ret)

    uid = request.args.get("uid")
    with SessionWrapper() as sess:
        exams = sess.query(BSRExam).filter_by(uid=uid)

        ret_exams = []
        for exam in exams:
            ret_exams.append({
                'create_time': exam.create_time.strftime("%Y%m%d"),
                'type_a': exam.type_a,
                'type_b': exam.type_b,
                'number': exam.number,
                'result': exam.result,
                'mister': exam.mister
            })

        ret = {
            'code': 200,
            'exams': ret_exams
        }
        return json.dumps(ret)


class BSRProfile(Base):
    __tablename__ = 'profile'

    uid = Column(Integer, primary_key=True)
    openid = Column(String)
    name = Column(String)
    icon = Column(String)
    wid = Column(String)
    create_time = Column(DateTime)
    gender = Column(String)


class BSRFootprint(Base):
    __tablename__ = 'footprint'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    create_time = Column(DateTime)
    description = Column(String)
    type = Column(String)
    duration = Column(String)


class BSRExam(Base):
    __tablename__ = 'exam'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    create_time = Column(DateTime)
    type_a = Column(String)
    type_b = Column(String)
    number = Column(Integer)
    result = Column(String)
    mister = Column(String)


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
