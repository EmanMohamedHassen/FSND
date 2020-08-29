import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  # set Access-Control-Allow
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  #Get all available categories.
  @app.route('/categories',methods=['GET'])
  def get_categories():
    page= request.args.get('page',1,type=int)
    start = (page - 1 )*10
    end = start + 10
    categories = Category.query.all()
    formatted_categories = [category.format() for category in categories]
    categoriesObject = {category.id:category.type for category in categories}

    if len(formatted_categories) == 0 :
      abort(404)

    return jsonify({
      'success':True,
      'categories':categoriesObject,
      'total_categories':len(formatted_categories)
    })

  #Get All Questions with Pagination
  @app.route('/questions',methods=['GET'])
  def questions():
    page=request.args.get('page',1,type=int)
    start = (page-1)*10
    end=start+10
    questions = Question.query.all()
    formatted_questions = [question.format() for question in questions]
    categories = {category.id:category.type for category in Category.query.all()}

    if len(formatted_questions) == 0 :
      abort(404)

    return jsonify({
      'success':True,
      'questions':formatted_questions[start:end],
      'total_questions':len(formatted_questions),
      'current_category':'',
      'categories':categories
    })

  #Delete a question
  @app.route('/questions/<int:id>',methods=['DELETE'])
  def delete_question(id) :
    try:
      question = Question.query.filter(Question.id == id).one_or_none()

      if question is None :
        abort(404)
      question.delete()
      
      return jsonify({
        'success': True,
        'deleted_question': id
      })
    except:
      abort(422)

  # Insert a new question
  @app.route('/questions',methods=['POST'])
  def add_question():
    body = request.get_json()
    question_text= body.get('question',None)
    answer = body.get('answer',None)
    difficulty = body.get('difficulty',None)
    category = body.get('category',None)
    try:
      question = Question(question=question_text,answer=answer,difficulty=difficulty,category=category)
      question.insert()

      return jsonify({
        'success': True,
        'createdQuestion':question.id
      })
    except:
      abort(422)
      

  # Search Questions List
  @app.route('/questions/<string:searchTerm>',methods=['POST'])
  def search_question(searchTerm):
    search = "%{}%".format(searchTerm.lower())
    questions = Question.query.filter(Question.question.ilike(search)).all()
    formatted_questions = [question.format() for question in questions]
    categories = {category.id:category.type for category in Category.query.all()}

    if len(formatted_questions) == 0 :
      abort(404)

    return jsonify({
      'success':True,
      'questions':formatted_questions,
      'total_questions':len(formatted_questions),
      'current_category':'',
      'categories':categories
    })
  
  #Get Questions List Accordding to Category
  @app.route('/categories/<int:id>/questions',methods=['GET'])
  def get_questions(id) :
    try:
      questions = Question.query.filter(Question.category == id).all()
      formatted_questions = [question.format() for question in questions]
      current_category=Category.query.filter_by(id=id).first()

      if len(formatted_questions) == 0 :
        abort(404)

      return jsonify({
        'success':True,
        'questions':formatted_questions,
        'total_questions':len(formatted_questions),
        'current_category':current_category.type
      })
    except:
      abort(422)
  #Get A random Question For Quiz
  @app.route('/quizzes', methods=['POST'])
  def get_quizzes():
      try:
          body = request.get_json()
          previous_questions = body.get('previous_questions', None)
          quiz_category = body.get('quiz_category', None)
          if quiz_category['id'] == 0:
              questions = Question.query.filter(
                Question.id.notin_(previous_questions)
                ).all()
          else:
              questions = Question.query.filter(
                Question.category == quiz_category['id'],
                Question.id.notin_(previous_questions)
                ).all()
          formatted_questions = [question.format() for question in questions]
          if len(formatted_questions) == 0:
              return jsonify({
                  'success': True,
                  })
          random_question = random.choice(formatted_questions)
          return jsonify({
              'success': True,
              'question': random_question
          })
      except:
          abort(422)

  #Handling Errors

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "Not found"
          }), 404

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
  
  return app

    