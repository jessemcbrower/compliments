import random
from flask import Flask
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, '/')

compliments = ['You look so nice today!', 'Where did you get that shirt? It looks so good on you!', 'I like what you did with your hair today!']

@ask.launch
def launch():
	compliment = random.choice(compliments)
	return statement(compliment)