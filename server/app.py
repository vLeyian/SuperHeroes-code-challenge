#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource 
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Heroes(Resource):
    def get(self):
        heroes = [hero.to_dict() for hero in Hero.query.all()]
        for hero in heroes:
            hero.pop('hero_powers', None)
        return make_response(heroes, 200)
    
api.add_resource(Heroes, '/heroes')

class HeroByID(Resource):
    def get(self, id):
        hero = Hero.query.filter_by(id=id).first()
        if hero is None:
            return {"error": "Hero not found"}, 404
        response_dict = hero.to_dict()
        return response_dict, 200

api.add_resource(HeroByID, '/heroes/<int:id>')

class Powers(Resource):
    def get(self):
        response_dict_list = [power.to_dict() for power in Power.query.all()]
        return make_response(response_dict_list, 200)
    
api.add_resource(Powers, '/powers')

class PowerByID(Resource):
    def get(self, id):
        power = Power.query.filter_by(id=id).first()
        if power is None:
            return {"error": "Power not found"}, 404
        response_dict = power.to_dict()
        return response_dict, 200

    def patch(self, id):
        power = Power.query.filter_by(id=id).first()
        if power is None:
            return {"error": "Power not found"}, 404
        data = request.get_json()
        if 'description' in data:
            try:
                power.description = data['description']
                db.session.commit()
                return power.to_dict(), 200
            except AssertionError:
                return {"errors": ["validation errors"]}, 400
        else:
            return {"errors": ["validation errors"]}, 400

api.add_resource(PowerByID, '/powers/<int:id>')

class HeroPowers(Resource):
    def post(self):
        data = request.get_json()
        hero = Hero.query.get(data.get('hero_id'))
        power = Power.query.get(data.get('power_id'))
        if hero is None or power is None:
            return {"errors": ["validation errors"]}, 400
        if len(power.description) < 20:
            return {"errors": ["description must be at least 20 characters long"]}, 400
        try:
            hero_power = HeroPower(
                strength=data.get('strength'),
                hero_id=hero.id,
                power_id=power.id
            )
            db.session.add(hero_power)
            db.session.commit()
            response_dict = hero_power.to_dict()
            response_dict['hero'] = hero.to_dict()
            response_dict['power'] = power.to_dict()
            return response_dict, 200
        except AssertionError:
            return {"errors": ["validation errors"]}, 400

api.add_resource(HeroPowers, '/hero_powers')
        

if __name__ == '__main__':
    app.run(port=5555, debug=True)
