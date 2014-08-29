from flask import Flask, render_template, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from url_shortener import base_62
from urlparse import urlparse
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class Link(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(120))
	shortened = db.Column(db.String(50))
	visits = db.Column(db.Integer)

	def __init__(self, url, shortened=None):
		self.url = url
		self.shortened = shortened
		self.visits = 0

db.create_all()

@app.route('/')
def home():
	links = Link.query.all()
	print [l.shortened for l in links]
	return render_template('index.html')

@app.route('/', methods=['POST'])
def shorten_url():
	url = request.form.get('url').strip()
	if not urlparse(url).scheme:
		url = 'http://' + url
	link = Link(url)
	db.session.add(link)
	db.session.commit()
	link.shortened = base_62(link.id + 100)
	db.session.commit()
	return render_template('index.html', url='http://' + request.host + '/' + link.shortened)

@app.route('/<shortened>')
def link(shortened):
	link = Link.query.filter_by(shortened=shortened).first()
	return redirect(link.url)

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)