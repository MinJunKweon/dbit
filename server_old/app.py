#-*- coding: utf-8 -*-

from flask import Flask, Response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import urllib2
import json
import hashlib
import hmac
import xlrd
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://[db_route]'
db = SQLAlchemy(app)
ma = Marshmallow(app)
fb_graph = "https://graph.facebook.com"
fb_secret = "[fb_secret]"

class Semester(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True)
	key = db.Column(db.String(80), unique=True)
	version = db.Column(db.Integer)

	def __init__(self, name):
		self.name = name

class SemesterSchema(ma.ModelSchema):
	class Meta:
		model = Semester

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fbid = db.Column(db.BigInteger, unique=True)
	username = db.Column(db.String(20), unique=True)
	email = db.Column(db.String(50), unique=True)

	def __init__(self, fbid):
		self.fbid = fbid

class UserSchema(ma.ModelSchema):
	class Meta:
		 model = User

class Lecture(db.Model):
	id = db.Column(db.BigInteger, primary_key=True)
	semester_id = db.Column(db.Integer)
	lecture_course = db.Column(db.String(10))
	lecture_key = db.Column(db.String(20))
	lecture_name = db.Column(db.String(100))
	lecture_prof = db.Column(db.String(100))
	lecture_campus = db.Column(db.Integer) # 서울 0 / 일산 1 / None 2
	lecture_daytime = db.Column(db.String(100))
	lecture_location = db.Column(db.Text)
	lecture_point = db.Column(db.Integer)
	lecture_type = db.Column(db.String(100))
	lecture_lang = db.Column(db.String(20))
	lecture_etc = db.Column(db.Text)

class LectureSchema(ma.ModelSchema):
	class Meta:
		model = Lecture

db.create_all()

@app.route("/api/semester", methods = ['GET'])
def api_semester():
	ss = SemesterSchema(many=True)
	d = ss.dump(Semester.query.all())
	resp = Response(json.dumps(d.data),status=200,mimetype="application/json")
	return resp

@app.route("/api/semester/<int:semester>", methods = ['GET'])
def api_semester_info(semester):
	ss = SemesterSchema()
	d = ss.dump(Semester.query.filter_by(id=semester).first())
	resp = Response(json.dumps(d.data),status=200,mimetype="application/json")
	return resp

@app.route("/api/lecture/list/<int:semester>", methods = ['GET'])
def api_lecture_list(semester):
	ls = LectureSchema(exclude=("semester_id",),many=True)
	d = ls.dump(Lecture.query.filter_by(semester_id=semester).all())
	resp = Response(json.dumps(d.data),status=200,mimetype="application/json")
	return resp

@app.route("/api/user", methods = ['POST'])
def api_user():
	q = hmac.new(fb_secret, request.form.get('access_token'), hashlib.sha256).hexdigest()
	fbreq = urllib2.urlopen(fb_graph+"/me?fields=id,name,email&access_token="+request.form['access_token']+"&appsecret_proof="+q)
	fbdata = json.load(fbreq)
	u = User.query.filter_by(fbid=fbdata['id']).first()
	if u:
		resp = Response(fbdata,status=200,mimetype="application/json")
	else:
		u = User(fbid=fbdata['id'])
		if fbdata['email']:
			u.email = fbdata['email']
		db.session.add(u)
		db.session.commit()
		resp = Response(fbdata,status=200,mimetype="application/json")
	return resp

@app.route("/api/admin/add/semester", methods = ['GET'])
def admin_add_semester():
	year = int(request.args.get('year',0))
	semester = int(request.args.get('semester',0))
	if year==0 and semster==0:
		resp = Response("{'response':'404'}",status=200,mimetype="application/json")
	else:
		s = Semester.query.filter_by(name=str(year)+"년 "+str(semester)+"학기").first()
		if s: # 업데이트
			resp = Response("{'response':'Exists'}",status=200,mimetype="application/json")
		else: # 데이터 추가
			s = Semester(str(year)+"년 "+str(semester)+"학기")
			db.session.add(s)
			db.session.commit()
			workbook = xlrd.open_workbook(unicode(str(year)+"년 "+str(semester)+"학기"+".xls",'utf-8'))
			sheet = workbook.sheet_by_index(0)
			for i in range(sheet.nrows-1):
				if i != 0:
					l = Lecture()
					l.semester_id = s.id
					l.lecture_course = sheet.cell_value(i,1)
					l.lecture_key =  sheet.cell_value(i,3)
					l.lecture_name =  sheet.cell_value(i,4)
					l.lecture_prof =  sheet.cell_value(i,5)
					if unicode("서울",'utf-8') in sheet.cell_value(i,6):
						c = 0
					elif unicode("일산",'utf-8') in sheet.cell_value(i,6):
						c = 1
					else:
						c = 2
					l.lecture_campus = c # 서울 0 / 일산 1 / None 2
					l.lecture_daytime = sheet.cell_value(i,7)
					l.lecture_location = sheet.cell_value(i,8)
					l.lecture_point = int(sheet.cell_value(i,9))
					l.lecture_type = sheet.cell_value(i,16)
					l.lecture_lang = sheet.cell_value(i,17)
					l.lecture_etc = sheet.cell_value(i,21)
					db.session.add(l)
					db.session.commit()
			resp = Response("{'response':'200'}",status=200,mimetype="application/json")
	return resp

if __name__ == "__main__":
	app.run(debug=True)
