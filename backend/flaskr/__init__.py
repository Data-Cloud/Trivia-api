# from ast import FormattedValue
from genericpath import exists
import json
from functools import total_ordering
from operator import methodcaller
import os
import unittest
# from select import select
from urllib import response
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def object_category(selection):
    categories = {}
    for category in selection:
        format_categories = category.format()
        categories[f'{format_categories[0]}'] = format_categories[1]

    return categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response



    @app.route("/categories", methods=['GET'])
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all() 
        select = [selects.format() for selects in selection]       

        categories = object_category(selection)
        if len(selection) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "categories": categories
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
     """
    @app.route("/questions", methods=['GET'])
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories_selection = Category.query.order_by(Category.id).all()        
        categories = object_category(categories_selection)

        if len(current_questions) == 0:
            abort(404)

        # This endpoint should return a list of questions,
        # number of total questions, current category, categories.
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': [],
            'categories': categories,
        }), 200


    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):  
        if Question.query.get(question_id) is not None:
            try:
                question = Question.query.get(question_id)
                question.delete()
                all_questions = Question.query.all()
                return jsonify(({
                    "success":True,
                    "deleted": question_id,
                    "total_questions": len(all_questions),
                    "questions": [ques.format() for ques in all_questions]
                    }))
            except:
                abort(422)
        else:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route('/questions', methods=['POST'])
    def add_questions():
        question_body=request.get_json()
        if ('question' in question_body  and 'answer' in question_body and 'difficulty' in question_body and'category' in question_body):

            try:
                new_question = question_body.get('question')
                new_answer = question_body.get('answer')
                new_difficulty = question_body.get('difficulty')
                new_category = question_body.get('category')

                ques = Question(question=new_question, answer=new_answer,
                                category=new_category, difficulty=new_difficulty)

                ques.insert()
                return jsonify({
                    "success": True,
                    "created": ques.id
                        # Question.query.get(ques.id)
                })
            except:
                abort (422)
        else:
            abort (422)
    """
    

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    'of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    """
    @app.route('/questions/search', methods=['POST'])
    def search_params():
        search_body = request.get_json()
        if ('searchTerm' in search_body):
            try:
                search_term = search_body.get('searchTerm')
                if search_term:
                    search_results = Question.query.filter(
                        Question.question.ilike(f'%{search_term}%')).all()
                    res = paginate_questions(request,search_results)
                    return jsonify({
                        'success': True,
                        'questions': res,
                        'total_questions': len(res),
                        'current_category': None
                    })
            except:
                abort (422) 
        else:
            abort(404)
        # return len(search_body)
    """

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_by_category(category_id):
        try:
            
            ques = Question.query.filter(
                Question.category==str(category_id)).all()
            que = paginate_questions(request, ques)
            print(que) 
            return jsonify({
                "success":True,
                "questions": que,
                "total_questions": len(ques),
                "current_category": category_id
                })

        except:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    """
    @app.route('/quizzes', methods=['POST'])
    def get_quizzes():
        # This endpoint should take category and previous question parameters
        
        body = request.get_json()
        if not ('previous_questions' in body):
            abort(422)
        try:
            quiz_cat = body.get('quiz_category', None)
            previous_ques = body.get('previous_questions', None)
            category_id = quiz_cat['id']

            if category_id == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_ques)).all()
            else:
                questions = Question.query.filter(
                    Question.id.notin_(previous_ques),
                    Question.category == category_id).all()
            question = None
            if(questions):
                question = random.choice(questions)
                # print(type(question.format()['category']))
            return jsonify({
                'success': True,
                'question': question.format()
            })

        except:
            abort(422)
    """
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    # error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not Processable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500
    
    return app

