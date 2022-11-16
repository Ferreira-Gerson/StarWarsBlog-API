"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favourite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#USER

@app.route('/user', methods=['GET'])
def handle_hello():
   all_users = User.query.all()
   if len(all_users) == 0:
        return jsonify({"msg":"No users registered"}),500
   else:
        all_users = list(map(lambda x: x.serialize(), all_users))
        json_text = jsonify(all_users)
        return json_text
        
        return jsonify(response_body), 200

#People

@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    all_people = list(map(lambda x: x.serialize(), all_people))
    json_text = jsonify(all_people)
    return json_text

@app.route('/people/<int:id>', methods=['GET'])
def get_people_id():
   
    get_body_character= People.query.get(id)

    return jsonify({'char': [get_body_character.serialize()]}), 200

#Planets

@app.route('/planet', methods=['GET'])
def get_planets():
    all_planets = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), all_planets))
    json_text = jsonify(all_planets)
    return json_text, 200

@app.route('/planet/<int:id>', methods=['GET'])
def get_planet(id):
    get_body_planet= Planet.query.get(id)

    return jsonify({'planet': [get_body_planet.serialize()]}), 200

#Favorite
@app.route('/favourite/planet/<int:planet_id>', methods=['POST'])
def add_favourite_planet(planet_id):
    
    active_user = User.query.filter_by(is_active=True).first()
    check_fav = Favourite.query.filter_by(user_id=active_user.id, planet_id=planet_id).first()

    try:
        check_planet = Planet.query.get(planet_id)
        if check_planet == None:
            raise ValueError()
    except ValueError:
        return jsonify({"msg":"The planet doesnt exist in the database"}),400

    try:
        new_favourite_planet = Favourite(user_id=active_user.id, planet_id=planet_id)
        if check_fav != None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"The user already has this planet as favourite"}),500
    else:
        db.session.add(new_favourite_planet)
        db.session.commit()
        return jsonify(new_favourite_planet.serialize()),200



@app.route('/favourite/people/<int:character_id>', methods=['POST'])
def add_favourite_character(character_id):

    active_user = User.query.filter_by(is_active=True).first()
    checkFav = Favourite.query.filter_by(user_id=active_user.id, character_id=character_id).first()
    try:
        checkChar = People.query.get(character_id)
        if checkChar == None:
            raise ValueError()
    except ValueError:
        return jsonify({"msg":"The character doesnt exist in the database"}),400

    try:
        new_favourite_character = Favourite(user_id=active_user.id, character_id=character_id)
        if checkFav != None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"The user already has this character as favourite"}),500
    else:
        db.session.add(new_favourite_character)
        db.session.commit()
        return jsonify(new_favourite_character.serialize()),200

@app.route('/favourite/planet/<int:planet_id>', methods = ['DELETE'])
def delete_favourite_planet(planet_id):
    active_user = User.query.filter_by(is_active=True).first()
    try:
        checkPlanet = Planet.query.get(planet_id)
        if checkPlanet == None:
            raise ValueError()
    except ValueError:
        return jsonify({"msg":"The planet doesnt exist in the database"}),400
    try:
        user_fav_planet = Favourite.query.filter_by(user_id=active_user.id, planet_id=planet_id).first()
        if user_fav_planet == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"This user doesnt have this planet as favourite"}),500
    else:
        db.session.delete(user_fav_planet)
        db.session.commit()
        return jsonify(user_fav_planet.serialize()),200



@app.route('/favourite/people/<int:character_id>', methods = ['DELETE'])
def delete_favourite_character(character_id):
    active_user = User.query.filter_by(is_active=True).first()
    try:
        checkChar = People.query.get(character_id)
        if checkChar == None:
            raise ValueError()
    except ValueError:
        return jsonify({"msg":"The character doesnt exist in the database"}),400

    try:
        user_fav_character = Favourite.query.filter_by(user_id=active_user.id, character_id=character_id).first()
        if user_fav_character == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"This user doesnt have this character as favourite"}),500
    else:
        db.session.delete(user_fav_character)
        db.session.commit()
        return jsonify(user_fav_character.serialize()),200

@app.route('/user/favourite', methods=['GET'])
def get_fav():
    active_user = User.query.filter_by(is_active=True).first()
    try:
        if active_user == None:
            raise Exception()
    except Exception:
        return jsonify({"msg":"No user is active"}),500
    else:
        fav = Favourite.query.filter_by(user_id=active_user.id)
        fav = list(map(lambda x: x.serialize(), fav))

        return jsonify(fav),200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
