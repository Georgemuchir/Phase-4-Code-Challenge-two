#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes')
def heroes():
    heroes = [{"id": hero.id, "name": hero.name, "super_name": hero.super_name} for hero in Hero.query.all()]
    return jsonify(heroes), 200

@app.route('/heroes/<int:id>')
def hero_by_id(id):
    hero = Hero.query.get(id)
    if hero:
        return jsonify(hero.to_dict()), 200
    return jsonify({"error": "Hero not found"}), 404

@app.route('/powers')
def powers():
    powers = [{"id": power.id, "name": power.name, "description": power.description} for power in Power.query.all()]
    return jsonify(powers), 200

@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def powers_by_id(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    if request.method == 'GET':
        return jsonify({"id": power.id, "name": power.name, "description": power.description}), 200

    if request.method == 'PATCH':
        data = request.json
        description = data.get('description')
        if len(description) < 20:
            return jsonify({'errors': ['validation errors']}), 400

        for key, value in data.items():
            setattr(power, key, value)
        db.session.commit()
        return jsonify(power.to_dict()), 200

@app.route('/hero_powers', methods=['GET', 'POST'])
def hero_powers():
    if request.method == 'GET':
        hero_powers = [hp.to_dict() for hp in HeroPower.query.all()]
        return jsonify(hero_powers), 200

    if request.method == 'POST':
        strength = request.json.get('strength')
        power_id = request.json.get('power_id')
        hero_id = request.json.get('hero_id')

        if strength not in ['Strong', 'Weak', 'Average']:
            return jsonify({"errors": ["validation errors"]}), 400

        new_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)
        db.session.add(new_power)
        db.session.commit()
        return jsonify(new_power.to_dict()), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
