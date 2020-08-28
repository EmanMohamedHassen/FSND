import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}:{}@{}/{}".format('eman','em1234','localhost:5434',self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        self.new_question={
            'question':"Who Invented the Automobile?",
            'answer':'Nicolas-Joseph',
            'difficulty':'2',
            'category':'1'
        }
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        result = self.client().get('/categories')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])

    def test_405_get_categories(self):
        result = self.client().delete('/categories')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"method not allowed")
        
    def test_get_questions(self):
        result = self.client().get('/questions')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    def test_405_get_questions(self):
        result = self.client().delete('/questions')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"method not allowed")

    def test_delete_question(self):
        result = self.client().delete('/questions/11')
        data=json.loads(result.data)
        question = Question.query.filter(Question.id == 11).one_or_none()
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question'],11)

    def test_422_delete_question(self):
        result = self.client().delete('/questions/100')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"unprocessable")

    def test_404_delete_question(self):
        result = self.client().post('/questions/10')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"Not found")
        
    def add_question(self):
        result = self.client().post('/questions',json=self.new_question)
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_add_question(self):
        result = self.client().post('/questions/100',json=self.new_question)
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"Not found")

    def search_question(self):
        result = self.client().post('/questions/what')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['total_questions']))

    def test_404_search_question(self):
        result = self.client().post('/questions/hello')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"Not found")

    def get_questions_by_categoryId(self):
        result = self.client().get('/categories/1/questions')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['total_questions']))
        self.assertEqual(data['current_category'],1)

    def test_422_get_questions_by_categoryId(self):
        result = self.client().get('/categories/100/questions')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"unprocessable")
        
    def get_quizzes(self):
        result = self.client().POST('/quizzes')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
    def test_405_get_quizzes(self):
        result = self.client().delete('/quizzes')
        data=json.loads(result.data)
        self.assertEqual(result.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],"method not allowed")
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()