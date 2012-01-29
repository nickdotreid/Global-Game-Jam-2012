from flask import Flask, redirect, request, flash, render_template, session, jsonify, Blueprint, url_for, g
import os

from database import db_session
from models import *

from sms import send_sms

app = Flask(__name__)
app.secret_key = os.environ['ggj12_secret_key']

@app.route("/",methods=['GET', 'POST'])
def home_page():
	login()
	return render_template("pages/signup.html")

@app.route("/start",methods=['GET','POST'])
def start_game():
	login()
	if not g.player or g.player is None:
		return redirect("/")
	game = Game()
	db_session.add(game)
	game.players.append(g.player)
	db_session.commit()
	return redirect(url_for(".pick_players",key=game.short))

@app.route("/<key>/pick",methods=['GET','POST'])
def pick_players(key):
	login()
	game = Game.query.filter_by(short=key).first()
	if game is None:
		return redirect("/")
	if 'phone' in request.form:
		phone_number = format_phone_number(request.form['phone'])
		player = Player.query.filter_by(phone=phone_number).first()
		if player is None:
			player = Player(phone_number)
			if 'name' in request.form:
				player.name = request.form['name']
			db_session.add(player)
			db_session.commit()
		found = False
		for person in game.players:
			if person.id == player.id:
				found = True
				flash("Player is already in game")
		if not found:
			game.players.append(player)
			db_session.commit()
			return redirect(url_for(".draw_game",key=game.short,player_id=player.id))
	return render_template("pages/pick_players.html",game=game)

@app.route("/game/<key>",methods=['GET','POST'])
def draw_game(key):
	login()
	game = Game.query.filter_by(short=key).first()
	if game is None:
		return redirect("/")
	for player in game.players:
		if player.id != g.player.id:
			if Challenge.query.filter_by(game=game).filter_by(player=player).filter_by(completed=False).first() is None:
				return challenge_player(game.short)
	for challenge in game.challenges:
		if challenge.player.id == g.player.id:
			return game_challenge(game.short)
	return render_template("pages/game_view.html",game=game)
	

@app.route("/game/<key>/challenge",methods=['GET','POST'])
def challenge_player(key):
	login()
	game = Game.query.filter_by(short=key).first()
	if game is None:
		return redirect("/")
	if 'lat' in request.form and 'lng' in request.form and 'player_id' in request.form:
		player = Player.query.filter_by(id=request.form['player_id']).first()
		if player is None:
			flash("Player does not exist","error")
			return redirect(url_for(".draw_game",key=game.short))
		challenge = Challenge(game,player,request.form['lat'],request.form['lng']);
		db_session.commit()
		send_sms(player.phone,"You got a challenge"+make_game_link(game.short))
		flash("Player has been challenged","success")
		return redirect(url_for(".draw_game",key=game.short))
	return render_template("pages/challenge_player.html",game=game)

@app.route("/game/<key>/my_challenge",methods=['GET','POST'])
def game_challenge(key):
	login()
	game = Game.query.filter_by(short=key).first()
	if game is None:
		return redirect("/")
	if 'lat' in request.form and 'lng' in request.form and 'challenge_id' in request.form:
		return check_challenge_answer()
	for challenge in game.challenges:
		if challenge.player.id == g.player.id and not challenge.completed:
			return render_template("pages/game_challenge.html",challenge=challenge,player=g.player,game=game)
	return render_template("pages/game_view.html",game=game)

def check_challenge_answer():
	login()
	if 'challenge_id' in request.form:
		challenge = Challenge.query.filter_by(id=request.form['challenge_id']).first()
		if challenge is not None:
			challenge.completed = True
			db_session.commit()
			flash("You completed the challenge")
			#send sms to all other game players
			for player in challenge.game.players:
				if player.id != g.player.id:
					send_sms(player.phone," has completed their challenge in "+make_game_link(challenge.game.short))
			return redirect(url_for(".draw_game",key=challenge.game.short))
	return redirect("/")

@app.route("/games")
def list_games():
	login()
	if g.player is None:
		return redirect("/")
	games = g.player.games
	return render_template('pages/games_list.html',games=games,player=g.player)

@app.route("/signup",methods=['GET','POST'])
def signup():
	if 'phone' in request.form:
		phone_number = format_phone_number(request.form['phone'])
		player = Player.query.filter_by(phone=phone_number).first()
		if player is None:
			player = Player(phone_number)
			db_session.add(player)
			db_session.commit()
		if 'name' in request.form:
			player.name = request.form['name']
			db_session.commit()
		session['player_id'] = player.id
		g.player = player
		return redirect(url_for(".list_games"))
	return render_template("pages/signup.html")	

@app.route("/login",methods=['GET','POST'])
def do_login():
	login()
	if 'phone' in request.form:
		player = Player.query.filter_by(phone=request.form['phone']).first()
		if player is not None:
			session['player_id'] = player.id
			g.player = player
			return redirect(url_for(".list_games"))
	return render_template("pages/login.html")

@app.route("/track",methods=['GET','POST'])
def view_track_location():
	login()
	if 'player_id' in session:
		if track_location(g.player):
			return jsonify({'success':True})
	return jsonify({'success':False})

def track_location(player):
	if 'lat' in request.form and 'lng' in request.form:
		location = Location(player,request.form['lat'],request.form['lng'])
		db_session.add(location)
		db_session.commit()
		return location
	return False
	
def login():
	g.player = None
	if 'phone' in request.args:
		player = Player.query.filter_by(phone=request.args['phone']).first()
		if player is None:
			player = Player(request.args['phone'])
			db_session.add(player)
			db_session.commit()
		session['player_id'] = player.id
	if 'player_id' in session:
		player = Player.query.filter_by(id=session['player_id']).first()
		if player is not None:
			g.player = player
			return player
	return None

def is_valid_number(num):
	return True

def format_phone_number(num):
	# remove ( ) - . +1
	num = num.replace('(','').replace(')','').replace('-','').replace('.','').replace('+1','')
	while len(num)<10:
		num += "0"
	return num

def pretty_phone_number(num):
	return num
	
def make_game_link(key):
	return url_for(".draw_game",key=key)