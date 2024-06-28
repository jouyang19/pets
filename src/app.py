# our main flask app
# API == Application Program Interface

# can start flask with
# flask --app src/app.py run --port 5555 --debug

# can also use env vars (don't commit the .env file!!!)
# export FLASK_APP=src/app.py
# export FLASK_RUN_PORT=5555
# export FLASK_DEBUG=1
# flask run

# HTTP Verbs: POST, GET, PATCH (PUT), DELETE
# ReST - Representational State Transfer

from flask import Flask, make_response, jsonify, request
from models import db, Pet, Owner
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # how to connect to the db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # optional performance thing

db.init_app(app)  # link sqlalchemy with flask
Migrate(app, db)  # set up db migration tool (alembic)


@app.route('/')
def hello():
    json_string = jsonify({'test': 'hello'})  # turn dict into json
    web_resp = make_response(json_string, 200)  # build a web resp
    return web_resp


@app.route('/test')
def test():
    return {'result': 'test'}, 200


# we can add parameters to our routes
@app.route('/upper/<string:word>')
def upper(word):
    new_word = word.upper()
    return {'result': new_word}, 200


@app.route('/dogs')
def dogs():
    # query db for all dog pets
    all_dogs = Pet.query.filter(Pet.type == 'dog').all()
    all_dog_dicts = [d.to_dict() for d in all_dogs]  # turn all dog objs into dicts
    return all_dog_dicts, 200

@app.route('/pets', methods=['GET', 'POST'])
def all_pets():
    if request.method == "GET":
        pets = Pet.query.all()
        return [p.to_dict() for p in pets], 200
    elif request.method == "POST":
        data = request.get_json()
        
        try: #try to run this block of code 
            new_pet = Pet(
                name = data.get('name'), # data['field_key'] will crash the server whereas data.get() will not and instead will input None if there is no value stored for said key
                age = data.get('age'),
                type = data.get('type'),
                owner_id = data.get('owner_id')
            )
        except ValueError as e: #if a ValueError is raise above, run this code; Bad practice to use Exception, because Value Error and other errors are subclasses of Exception Error.
            return {'error': str(e)}, 400
        
        db.session.add(new_pet) # do not forget to add pet to db environment and save it to db!
        db.session.commit()
        return new_pet.to_dict(), 201

@app.route('/pets/<int:id>', methods=['GET', 'PATCH', "DELETE"])
def pet_by_id(id):
    pet = Pet.query.filter(Pet.id == id).first()
    if not pet:
            return {'error': 'pet not found'}, 404
        
    if request.method == "GET":
        return pet.to_dict(), 200
    
    if request.method == "PATCH":
        
        data = request.get_json() # get json data from request
        
        # option 1, check every single field
        # if 'name' in data:
        #     pet.name = data.get('name')
        # elif 'age' in data:
        #     pet.age = data.get('age')
        # elif 'type' in data:
        #     pet.type = data.get('type')
        
        #option 2
        for field in data: # this way is much shorter, checks if each field exists, if so, update only those fields
            # pet.field = data[field] # DOESN'T WORK
            try:
                setattr(pet, field, data[field]) 
            except ValueError as e:
                return {"error": str(e)}, 400
            
        db.session.add(pet)
        db.session.commit()
        
        return pet.to_dict(), 200
    
    elif request.method == "DELETE":
        db.session.delete(pet)
        db.session.commit()
        
        return {}, 200
        
        
        
