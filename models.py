from sqlalchemy import Column, Integer, Float, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from database import Base

game_to_player = Table('game_to_player',Base.metadata,
	Column('players_id',Integer,ForeignKey('players.id')),
	Column('games_id',Integer,ForeignKey('games.id')))

class Player(Base):
	__tablename__ = 'players'
	id = Column(Integer, primary_key=True)
	phone = Column(String(15))
	name = Column(String(120), nullable=True)
	
	locations = relationship('Location',backref="player")
	challenges = relationship('Challenge',backref="player")
	
	games = relationship("Game",
		secondary=game_to_player,
		backref="players")

	def __init__(self, phone):
		self.phone = phone
		
	def __repr__(self):
		return '<Player %r>' % (self.phone)
		
class Game(Base):
	__tablename__ = 'games'
	id = Column(Integer,primary_key=True)
	short = Column(String(12))
	challenges = relationship('Challenge',backref="game")
	
	def __init__(self):
		self.short = self.make_short()
	
	def make_short(self):
		key = make_random_string(10)
		if Game.query.filter_by(short=key).first() is not None:
			return make_short(self)
		return key
	
	def count_score(self):
		return 10
	
	def __repr__(self):
		return '<Game %r>' % (self.short)

class Location(Base):
	__tablename__ = 'locations'
	id = Column(Integer, primary_key=True)
	player_id = Column(Integer,ForeignKey('players.id'))
	time = Column(DateTime)
	lat = Column(Float)
	lng = Column(Float)
	
	def __init__(self,player,lat,lng):
		from datetime import datetime
		self.player = player
		self.time = datetime.now()
		self.lat = lat
		self.lng = lng

	def __repr__(self):
		return '<Location %r>' % (self.id)
	
class Challenge(Base):
	__tablename__ = 'challenges'
	id = Column(Integer, primary_key=True)
	player_id = Column(Integer,ForeignKey('players.id'))
	game_id = Column(Integer,ForeignKey('games.id'))
	time = Column(DateTime)
	lat = Column(Float)
	lng = Column(Float)
	completed = Column(Boolean)
	
	def __init__(self,game,player,lat,lng):
		from datetime import datetime
		self.game = game
		self.player = player
		self.time = datetime.now()
		self.lat = lat
		self.lng = lng
		self.completed = False

	def __repr__(self):
		return '<Challenge %r>' % (self.id)
		
def make_random_string(length):
	import string,random
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(length))
