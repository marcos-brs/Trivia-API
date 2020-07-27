import json
import unittest

from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "docker"
        self.database_host = "localhost"
        self.dabase_port = 5432
        self.database_path = "postgresql://{}:{}@{}:{}/{}".format(
            self.database_user, self.database_password, self.database_host, self.dabase_port, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

        self.assertTrue(data['total_questions'] <= 10)

    def test_delete_question_that_does_not_exist(self):
        res = self.client().delete('/questions/1')
        # question 1 does not exist
        self.assertEqual(res.status_code, 422)

    def test_delete_question_that_exist(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)

        # question 2 exist
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 4)

    def test_create_question_with_missing_params(self):
        res = self.client().post('/questions', json={
            "question": "test",
            "answer": "test",
            "difficulty": 2,
            #   "category": 1,  =>  without category for example
        })

        self.assertEqual(res.status_code, 422)

    def test_create_question_with_all_params(self):
        res = self.client().post('/questions', json={
            "question": "test",
            "answer": "test",
            "difficulty": 2,
            "category": 1
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_search_question_that_does_not_exist(self):
        res = self.client().post('/search_questions', json={
            'search_term': '66666666'
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)

    def test_search_question_that_exist(self):
        res = self.client().post('/search_questions', json={
            'search_term': 'title'
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'] > 0)

    def test_list_questions_by_category_id_that_does_not_exist(self):
        res = self.client().get('/categories/666/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(data['questions'])
        self.assertEqual(data['total_questions'], 0)

    def test_list_questions_by_category_id_that_exist(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])

    def test_play_quiz(self):
        res = self.client().post('/quiz', json={
            "quiz_category": {
                "type": "click",
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_play_quiz_with_category(self):
        res = self.client().post('/quiz', json={
            "quiz_category": {
                "type": "science",
                "id": "1"
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual((data['question'])['category'], 1)

    def test_play_quiz_with_previous_questions(self):

        end_quiz = False
        previous_questions = []

        while end_quiz == False:
            res = self.client().post('/quiz', json={
                "quiz_category": {
                    "type": "click"
                },
                "quiz_previous_questions": previous_questions
            })

            if res.status_code != 200:
                end_quiz = True
                break

            data = json.loads(res.data)
            previous_questions.append((data['question'])['id'])

        # after pass for all questions
        self.assertEqual(res.status_code, 422)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
