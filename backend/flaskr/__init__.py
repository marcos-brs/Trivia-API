import random

from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__)
    setup_db(app)

    '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    '''
  Create an endpoint to handle GET requests
  for all available categories.
  '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        # check if has data
        if len(categories) == 0:
            abort(404)

        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    '''
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''

    @app.route('/questions', methods=['GET'])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()

        # check if has data
        if len(questions) == 0:
            abort(404)

        categories = Category.query.order_by(Category.id).all()
        formatted_categories = {
            category.id: category.type for category in categories}

        page = int(request.args.get('page', '1'))

        lower_limit = (page - 1) * QUESTIONS_PER_PAGE
        upper_limit = lower_limit + QUESTIONS_PER_PAGE

        formatted_questions = [question.format()
                               for question in questions[lower_limit:upper_limit]]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': None,
            'categories': formatted_categories,
        })

    '''
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
        except:
            abort(422)

        return jsonify({
            'success': True,
            'deleted': question_id
        })

    '''
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        if body == None:
            abort(422)

        requiered_params = ['question', 'answer', 'difficulty', 'category']

        for param in requiered_params:
            if param not in body:
                abort(422)

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        try:
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)
            question.insert()

        except:
            abort(422)

        return jsonify({
            'success': True,
            'created': question.id,
        })

    '''
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

    @app.route('/search_questions', methods=['POST'])
    def search_question():
        body = request.get_json()

        if body == None:
            abort(422)
        elif body.get('search_term') == None:
            abort(422)

        search_term = body.get('search_term')

        questions = Question.query.filter(
            Question.question.ilike('%{}%'.format(search_term))).all()

        formatted_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(questions),
            'current_category': None
        })

    '''
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def list_questions_by_category(category_id):

        try:
            questions = Question.query.filter_by(
                category=str(category_id)).all()
            formatted_questions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(questions),
                'current_category': None
            })
        except:
            abort(404)

    '''
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

    @app.route('/quiz', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()

            category = body.get('quiz_category')
            previous_questions = body.get('quiz_previous_questions', [0])

            if category['type'] == 'click':
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter_by(category=category['id']).filter(
                    Question.id.notin_(previous_questions)).all()

            formatted_questions = [question.format() for question in questions]

            if formatted_questions == []:
                abort(422)

            new_question = formatted_questions[random.randrange(
                0, len(formatted_questions))] if len(formatted_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)

    '''
  Create error handlers for all expected errors
  including 404 and 422.
  '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    return app
