from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_all_drinks():
    try:
        drinks = Drink.query.all()
        drinks = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drink': drinks
        }), 200

    except:
        abort(422)

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drink': drinks
        }), 200
    except:
        abort(422)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        data = request.get_json()['title'] and request.get_json()['recipe']
        if not data:
            abort(400)
    except (TypeError, KeyError):
        abort(400)

    # check if drink title exists
    if Drink.query.filter_by(title=request.get_json()['title']).first():
        abort(409)

    try:
        Drink(
            title=request.get_json()['title'],
            recipe=json.dumps(request.get_json()['recipe'])
        ).insert()
        drink = Drink.query.filter_by(title=request.get_json()['title']).first()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 201
    except:
        abort(422)

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    drink = Drink.query.filter_by(id=id).first()
    if not drink:
        abort(404)
        
    try:
        data = request.get_json()['title'] and request.get_json()['recipe']
        if not data:
            abort(400)
    except (TypeError, KeyError):
        abort(400)
    
    # check if drink title exists
    if Drink.query.filter_by(title=request.get_json()['title']).first():
        abort(409)

    try:
        if request.get_json().get('title'):
            drink.title=request.get_json()['title']

        if request.get_json().get('recipe'):
            drink.recipe=json.dumps(request.get_json()['recipe'])
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception:
        abort(422)


# Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404


@app.errorhandler(409)
def duplicate(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "Title already exists"
    }), 409


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code