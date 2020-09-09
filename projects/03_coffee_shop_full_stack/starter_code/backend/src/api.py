import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
the following line to initialize the datbase
THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
        a public endpoint
        returns a list of drinks
'''


@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.short() for drink in drinks]
        if len(formatted_drinks) == 0:
            return json.dumps({
                'success': False,
                'error': 'Drinks List is empty'
            }), 404

        return jsonify({
            'success': True,
            "drinks": formatted_drinks
        })
    except:
        abort(422)

'''
    GET /drinks-detail
        require the 'get:drinks-detail' permission
        returns a list of drinks details
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details():
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.long() for drink in drinks]
        if len(formatted_drinks) == 0:
            return json.dumps({
                'success': False,
                'error': 'Drinks List is empty'
            }), 404

        return jsonify({
            'success': True,
            "drinks": formatted_drinks
        })
    except:
        abort(422)

'''
    POST /drinks
        create a new row in the drinks table
        require the 'post:drinks' permission
        returns a list of drinks details
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            "drinks": drink.long()
        })
    except:
        abort(422)

'''
    PATCH /drinks/<id>
        update the corresponding row for <id>
        require the 'patch:drinks' permission
        returns a list of drinks details
'''


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(id):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            return json.dumps({
                'success': False,
                'error': 'Drink #' + id + ' not found to be edited'
            }), 404
        if title is not None:
            drink.title = title
        if recipe is not None:
            drink.recipe = json.dumps(recipe)
        drink.update()
        return jsonify({
             'success': True,
             "drinks": drink.long()
        })
    except:
        abort(422)

'''
    DELETE /drinks/<id>
        delete the corresponding row for <id>
        require the 'delete:drinks' permission
        returns  the id of the deleted record
'''


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            return json.dumps({
                'success': False,
                'error': 'Drink #' + id + ' not found to be edited'
            }), 404
        drink.delete()
        return jsonify({
                'success': True,
                "delete": id
        })
    except:
        abort(422)
# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
        }), 400


@app.errorhandler(405)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
        }), 405


@app.errorhandler(500)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

'''
error handler for AuthError
'''


@app.errorhandler(AuthError)
def unAuthorized(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
        }), error.status_code
