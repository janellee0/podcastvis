from flask import Flask
from flask import render_template
from flask import jsonify
import parse_json

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/naples')
def get_naples_entities():
	return jsonify(parse_json.get_entities('naples'))

@app.route('/easterntaiwan')
def get_easterntaiwan_entities():
	return jsonify(parse_json.get_entities('easterntaiwan'))

@app.route('/milwaukee')
def get_milwaukee_entities():
	return jsonify(parse_json.get_entities('milwaukee'))
