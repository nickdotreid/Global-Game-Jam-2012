from flask import Flask, redirect, request, flash, render_template, session, jsonify, Blueprint, url_for, g
import os

from database import db_session
from models import *

from sms import send_sms

app = Flask(__name__)
app.secret_key = os.environ['ggj12_secret_key']

@app.route("/",methods=['GET', 'POST'])
def home_page():
	if g.player:
		return redirect(url_for(".list_games"))
	return render_template("pages/home_page.html")

@app.route("/start",methods=['GET','POST'])
def start_game():
	if not g.player or g.player is None:
		return redirect("/")
	game = Game()
	db_session.add(game)
	game.players.append(g.player)
	db_session.commit()
	return redirect(url_for(".pick_players",key=game.short))

@app.route("/game/<key>/pick",methods=['GET','POST'])
def pick_players(key):
	game = Game.query.filter_by(short=key).first()
	if game is None:
		return redirect("/")
	player = None
	if 'player_id' in request.form and request.form!="new":
		player = get_player(id = request.form['player_id'])
	if 'phone' in request.form and player is None:
		player = get_player(phone = request.form['phone'], name = request.form['name'])
	if player is not None:
		if add_player_to_game(player,game):
			return redirect(url_for(".draw_game",key=game.short,player_id=player.id))
	friends = find_player_friends(g.player)
	return render_template("pages/pick_players.html",game=game,friends=friends)

def add_player_to_game(player,game):
	for person in game.players:
		if person.id == player.id:
			flash("Player is already in game")
			return False
	game.players.append(player)
	db_session.commit()
	return True

@app.route("/game/<key>",methods=['GET','POST'])
def draw_game(key):
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
		send_game_sms(player,game,g.player.name+" threw a ball at you")
		flash("You threw the ball to "+player.name+" at "+player.phone,"success")
		return redirect(url_for(".draw_game",key=game.short))
	players = []
	for player in game.players:
		if player.id != g.player.id:
			if Challenge.query.filter_by(game=game).filter_by(player=player).filter_by(completed=False).first() is None:
				players.append(player)
	return render_template("pages/challenge_player.html",game=game,players=players)

@app.route("/game/<key>/my_challenge",methods=['GET','POST'])
def game_challenge(key):
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
	if 'challenge_id' in request.form:
		challenge = Challenge.query.filter_by(id=request.form['challenge_id']).first()
		if challenge is not None:
			challenge.completed = True
			db_session.commit()
			flash("You caught the ball")
			for player in challenge.game.players:
				if player.id != g.player.id:
					name = player.phone
					if player.name and player.name is not None:
						name = player.name
					orig_name = challenge.player.phone
					if challenge.player.name and challenge.player.name is not None:
						orig_name = challenge.player.name
					send_game_sms(player,challenge.game,orig_name+" caught the ball. Quick, throw it back!")
			return redirect(url_for(".draw_game",key=challenge.game.short))
	return redirect("/")
	
@app.route("/challenge/<id>/delete",methods=['GET','POST'])
def challenge_delete(id):
	challenge = Challenge.query.filter_by(id=id).first()
	if challenge is not None:
		db_session.delete(challenge)
		db_session.commit()
		flash("Challenge has been removed")
		for player in challenge.game.players:
			if player.id != challenge.player.id:
				send_game_sms(player,challenge.game,challenge.player.name+" couldn't catch the ball. Give them something easier to catch.")
		return redirect(url_for(".draw_game",key=challenge.game.short))
	return redirect("/")

@app.route("/games")
def list_games():
	if g.player is None:
		return redirect("/")
	games = g.player.games
	games.reverse()
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
	if 'phone' in request.form:
		phone_number = format_phone_number(request.form['phone'])
		player = Player.query.filter_by(phone=phone_number).first()
		if player is not None:
			session['player_id'] = player.id
			g.player = player
			return redirect(url_for(".list_games"))
		flash("Could not login user","error")
	return render_template("pages/login.html")

@app.route("/logout")
def logout():
	session['player_id'] = None
	g.player = None
	return redirect(url_for(".home_page"))

@app.route("/track",methods=['GET','POST'])
def view_track_location():
	if 'player_id' in session:
		if track_location(g.player):
			return jsonify({'success':True})
	return jsonify({'success':False})

@app.before_request
def check_login():
	login()

def track_location(player):
	if 'lat' in request.form and 'lng' in request.form:
		location = Location(player,request.form['lat'],request.form['lng'])
		db_session.add(location)
		db_session.commit()
		return location
	return False

@app.route("/location/player",methods=['GET','POST'])
def get_location():
	if 'id' in request.form:
		player = get_player(id=request.form['id'])
		if player is not None and len(player.locations)>0:
			location = player.locations.pop()
			return jsonify({'id':request.form['id'],'lat':location.lat,'lng':location.lng})
	return jsonify({'success':False})

def get_player(id=False,phone=False,name=False):
	player = None
	if phone:
		phone_number = format_phone_number(phone)
		player = Player.query.filter_by(phone=phone_number).first()
	if id:
		player = Player.query.filter_by(id=id).first()
	if player is None and phone:
		player = Player(format_phone_number(phone))
		if name:
			player.name = name
		db_session.add(player)
		db_session.commit()
	return player

def find_player_friends(player):
	friends = []
	for game in player.games:
		for person in game.players:
			if person.id != player.id:
				friends.append(person)
	return friends

def login():
	g.player = None
	if 'phone' in request.args:
		player = get_player(phone=request.args['phone'])
		session['player_id'] = player.id
	if 'player_id' in session:
		player = get_player(id=session['player_id'])
		if player is not None:
			g.player = player
			return player
	return None

def is_valid_number(num):
	return True

def format_phone_number(num):
	# remove ( ) - . +1
	num = num.replace('(','').replace(')','').replace('-','').replace('.','').replace('+1','').replace(' ','')
	while len(num)<10:
		num += "0"
	return num

def pretty_phone_number(num):
	return num

def send_game_sms(player,game,message):
	message = message + "\n" + make_game_link(game.short,player.phone)
	send_sms(player.phone,message)

def make_game_link(key,phone=None):
	prefix = 'http://'
	if 'ggj12_prefix' in os.environ:
		prefix = os.environ['ggj12_prefix']
	link = prefix+url_for(".draw_game",key=key,phone=phone)
	return shorten_url(link)

def shorten_url(link):
	import bitly_api
	if 'ggj12_bitly_username' not in os.environ or 'ggj12_bitly_token' not in os.environ:
		return link
	username = os.environ['ggj12_bitly_username']
	token = os.environ['ggj12_bitly_token']
	bitly = bitly_api.Connection(username,token)
	try:
		data = bitly.shorten(link)
	except:
		pass
		return link
	return data['url']