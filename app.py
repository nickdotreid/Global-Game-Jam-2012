from flask import Flask, redirect, request, flash, render_template, session, jsonify, Blueprint
import twilio

from database import db_session
from models import *

app = Flask(__name__)
app.secret_key = 'secrect'

@app.route("/",methods=['GET', 'POST'])
def home_page():
	login_phone()
	return render_template("pages/home_page.html")
	
def login_phone():
	if 'phone' in request.args:
		# check if number valid
		player = Player.query.filter_by(phone=request.args['phone']).first()
		if player is None:
			player = Player(request.args['phone'])
			db_session.add(player)
			db_session.commit()
		session['player'] = player