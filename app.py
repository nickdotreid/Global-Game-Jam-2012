from flask import Flask, redirect, request, flash, render_template, session, jsonify, Blueprint, url_for
import twilio

from database import db_session
from models import *

app = Flask(__name__)
app.secret_key = 'secrect'

@app.route("/",methods=['GET', 'POST'])
def home_page():
	login_phone()
	return render_template("pages/signup.html")

@app.route("/start",methods=['GET','POST'])
def pick_players():
	login_phone()
	if 'target' in request.form:
		#check valid number
		player = Player.query.filter_by(phone=request.form['target']).first()
		if player is None:
			player = Player(request.form['target'])
			if 'name' in request.form:
				player.name = request.form['name']
			db_session.add(player)
			db_session.commit()
		game = Game()
		game.players.append(player)
		game.players.append(session['player'])
		db_session.add(game)
		db_session.commit()
		url = url_for(".start_game",key=game.short)
		return redirect(url)
	return render_template("pages/pick_players.html")
		

@app.route("/<key>/pick",methods=['GET','POST'])
def start_game(key):
	login_phone()
	game = Game.query.filter_by(short=key).first()
	if game is None:
		url = url_for(".home_page")
		return redirect(url)
	if 'lat' in request.form and 'lng' in request.form:
		location = track_location(session['player']) #not sure how this will work yet
	return render_template("pages/game_start.html",game=game)
	
@app.route("/track",methods=['GET','POST'])
def view_track_location():
	login_phone()
	if track_location(session['player']):
		return jsonify({'success':True})
	return jsonify({'success':False})

def track_location(player):
	if 'lat' in request.form and 'lng' in request.form:
		location = Location(player,request.form['lat'],request.form['lng'])
		db_session.add(location)
		db_session.commit()
		return location
	return False
	
def login_phone():
	if session['player']:
		return session['player']
	if 'phone' in request.args:
		# check if number valid
		player = Player.query.filter_by(phone=request.args['phone']).first()
		if player is None:
			player = Player(request.args['phone'])
			db_session.add(player)
			db_session.commit()
		session['player'] = player