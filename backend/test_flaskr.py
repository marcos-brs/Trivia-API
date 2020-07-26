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


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
