from flask import Flask, render_template, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from urlparse import urlparse
import os
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

char_set = list(string.ascii_letters) + [str(i) for i in range(10)]

class Link(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	url = db.Column(db.String(120))
	shortened = db.Column(db.String(50))
	visits = db.Column(db.Integer)

	def __init__(self, url, shortened=None):
		self.url = url
		self.shortened = shortened
		self.visits = 0

	def shorten(self):
		converted = []
		num = self.id + 100
		while(num > 0):
			rem = num % 62
			converted.append(char_set[rem])
			num /= 62
		self.shortened = ''.join(converted)

db.create_all()

@app.route('/')
def home():
	Link.query.all()
	prefix = _to_full_url(request.host) + '/'
	links = [(prefix + link.shortened, link.visits) for link in Link.query.all()]
	return render_template('index.html', links=links)

@app.route('/', methods=['POST'])
def shorten_url():
	url = _to_full_url(request.form.get('url').strip())

	found = Link.query.filter_by(url=url)
	if (found.count() > 0):
		link =  found.first()
	else:
		link = Link(url)
		db.session.add(link)
		db.session.commit()
		link.shorten()
		db.session.commit()
	return render_template('index.html', url=_to_full_url(request.host) + '/' + link.shortened)

@app.route('/<shortened>')
def link(shortened):
	found = Link.query.filter_by(shortened=shortened)
	if (found.count() == 0):
		return 'Invalid Path', 400
	link = found.first()
	link.visits += 1
	db.session.commit()
	return redirect(link.url)

def _to_full_url(url):
	if not urlparse(url).scheme:
		url = 'http://' + url
	return url

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)