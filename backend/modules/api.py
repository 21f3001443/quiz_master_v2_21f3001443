from flask_restful import Resource
from flask_restful import fields, marshal_with, marshal
from flask_restful import reqparse
from flask_restful import abort
from flask import jsonify, make_response
from flask_jwt_extended import create_access_token,create_refresh_token, jwt_required, get_jwt_identity, get_jwt

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

import logging
import bcrypt
from datetime import datetime

from modules import (
    User,
    Role,
    Subject,
    Chapter,
    Quiz,
    Question,
    Option,
    Response,
    db,
    jwt_denylist,
)

#############################################################
###################### Logging config #######################
#############################################################
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)
#############################################################
###################### Logging config #######################
#############################################################

#############################################################
##################### Helper functions ######################
#############################################################
class ProtectedResource(Resource):
    method_decorators = [jwt_required()]

class SecureResource(Resource):
    method_decorators = [jwt_required(optional=True)]

class TokenRefreshResource(Resource):
    method_decorators = [jwt_required(refresh=True)]

def date_type(value):
    try:
        # Parse string like "14:30" or "14:30:59"
        return datetime.strptime(value, "%Y-%m-%d")
        # If you also want seconds: "%H:%M:%S"
    except ValueError:
        raise ValueError(f"Invalid date format: {value}. Expected YYYY-MM-DD")

def time_type(value):
    try:
        # Parse string like "14:30" or "14:30:59"
        return datetime.strptime(value, "%H:%M").time()
        # If you also want seconds: "%H:%M:%S"
    except ValueError:
        raise ValueError(f"Invalid time format: {value}. Expected HH:MM")
    
def datetime_type(value):
    try:
        return datetime.fromisoformat(value)  # "2025-09-10T14:30:00"
    except ValueError:
        raise ValueError(f"Invalid datetime format: {value}. Expected ISO8601")

def global_create(schema, args, key, self):
    try:
        id = args.get(key)
        result = schema.query.filter_by(**{key: id}).first()
        if result:
            logging.error(f"{key}:{id} in {schema.__name__} already exists.")
            return {"error": f"{key}:{id} in {schema.__name__} already exists."}, 409

        obj = schema(**{key: id})
        for k, v in args.items():
            if v is not None and hasattr(obj, k):  # only update valid fields
                setattr(obj, k, v)
            if k == "password":
                setattr(obj, k, v)

        db.session.add(obj)
        db.session.flush()
        db.session.commit()

        logging.info(f"{key}:{id} in {schema.__name__} created.")
        return {"message": f"{key}:{id} in {schema.__name__} created."}, 201
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error occurred: {str(e)}")
        return {"error": "Database error occurred"}, e.code
    except Exception as e:
        if isinstance(e, HTTPException):
            logging.error(f"HTTP error occurred: {str(e)}")
            return {"error": "HTTP error occurred"}, e.code
        else:
            db.session.rollback()
            logging.error(f"Unexpected error occurred: {str(e)}")
            return {"error": "Unexpected error occurred"}, e.code

def global_read(schema, fields, key=None, value=None):
    try:
        # id = get_jwt_identity()
        # claim = get_jwt()
        # print(id)
        # print(claim)
        result = None
        if key and value:
            result = schema.query.filter_by(**{key: value}).first()
        else:
            result = schema.query.all()
        if not result:
            logging.error(f"{key} in {schema.__name__} not found ...!")
            return {"error": f"{key} in {schema.__name__} not found ...!"}, 404
        return marshal(result, fields), 200
    except SQLAlchemyError as e:
        logging.error(f"Database error occurred: {str(e)}")
        return {"error": "Database error occurred"}, e.code
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")
        return {"error": "Unexpected error occurred"}, e.code

def global_update(schema, args, key, self):
    try:
        id = args.get(key)
        result = schema.query.filter_by(**{key: id}).first()

        if result:
            for k, v in args.items():
                print(k, ":", v)
                print(type(k), ":", type(v))
                if v is not None and hasattr(result, k):  # only update valid fields
                    setattr(result, k, v)
                if k == "password":
                    setattr(result, k, v)

            db.session.commit()

            logging.info(f"{key}:{id} in {schema.__name__} updated.")

            return self.get(id)
        else:
            logging.error(f"{key}:{id} in {schema.__name__} not exist")
            return {"error": f"{key}:{id} in {schema.__name__} not exist"}, 404
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error occurred: {str(e)}")
        return {"error": "Database error occurred"}, e.code
    except Exception as e:
        if isinstance(e, HTTPException):
            logging.error(f"HTTP error occurred: {str(e)}")
            return {"error": "HTTP error occurred"}, e.code
        else:
            db.session.rollback()
            logging.error(f"Unexpected error occurred: {str(e)}")
            return {"error": "Unexpected error occurred"}, e.code

def global_delete(schema, key, value):
    try:
        result = schema.query.filter_by(**{key: value}).first()
        if result:
            db.session.delete(result)
            db.session.commit()
            logging.info(f"{key}:{value} in {schema.__name__} deleted.")
            return {"message": f"{key}:{value} in {schema.__name__} deleted."}, 200
        else:
            logging.error(f"{key}:{value} in {schema.__name__} not exist")
            return {"error": f"{key}:{value} in {schema.__name__} not exist"}, 404
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error occurred: {str(e)}")
        return {"error": "Database error occurred"}, e.code
    except Exception as e:
        if isinstance(e, HTTPException):
            logging.error(f"HTTP error occurred: {str(e)}")
            return {"error": "HTTP error occurred"}, e.code
        else:
            db.session.rollback()
            logging.error(f"Unexpected error occurred: {str(e)}")
            return {"error": "Unexpected error occurred"}, e.code

#############################################################
##################### Helper functions ######################
#############################################################

#############################################################
###################### Utilities ############################
#############################################################
user_password_login_template = reqparse.RequestParser()
user_password_login_template.add_argument("user_id", type=str, required=True)
user_password_login_template.add_argument("password", type=str, required=True)

class LoginRoute(SecureResource):
    def post(self):
        try:
            args = user_password_login_template.parse_args()
            user_id = args.get("user_id")
            user = User.query.filter_by(user_id=user_id).first()
            password = args.get("password")
            if user and user.user_id == user_id:
                if password:
                    if user.validate_password(password):
                        access_token = create_access_token(identity=user.user_id, additional_claims={"role": user.role.role_id}, fresh=True)
                        refresh_token = create_refresh_token(identity=user.user_id, additional_claims={"role": user.role.role_id})
                        logging.info(f"User '{user_id}' validated successfully.")
                        return {"message": "User validated successfully.", "access_token": access_token, "refresh_token": refresh_token}, 200
                    else:
                        logging.error(f"Invalid password for user '{user_id}'.")
                        return {"error": "Invalid password."}, 401
                else:
                    logging.error(f"Password not provided for user '{user_id}'.")
                    return {"error": "Password not provided."}, 400
            else:
                logging.error(f"User not found for ID: {user_id}")
                return {"error": "User not found"}, 404
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")
            return {"error": "Database error occurred"}, 500

class LoginPingRoute(ProtectedResource):
    def get(self):
        return {"message": "Pong"}, 200

class LoginRefreshRoute(TokenRefreshResource):
    def post(self):
        try:
            uid = get_jwt_identity()
            old_jwt = get_jwt()
            return {"message": "Refreshed token successfully.", "access_token": create_access_token(identity=uid, additional_claims={"role": old_jwt.get("role")})}, 200
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")
            return {"error": "Database error occurred"}, 500

class LogoutRoute(ProtectedResource):
    def post(self):
        try:
            jti = get_jwt()["jti"]
            jwt_denylist.add(jti)
            return {"message": "User logged out successfully."}, 200
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")
            return {"error": "Database error occurred"}, 500

class RegisterRoute(SecureResource):
    def post(self):
        print( user_create_template.parse_args())
        return global_create(User, user_create_template.parse_args(), "user_id", self)
        
quiz_question_template = reqparse.RequestParser()
quiz_question_template.add_argument("quiz_id", type=int, required=False)
quiz_question_template.add_argument("question_id", type=int, required=False)


class QuizesQuestionsRoute(ProtectedResource):
    def post(self):
        try:
            args = quiz_question_template.parse_args()
            quiz_id = args.get("quiz_id")
            question_id = args.get("question_id")

            quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
            if not quiz:
                logging.error(f"Quiz ID:{args.get('quiz_id')} not exist")
                return {"error": "quiz not exist"}, 404

            question = Question.query.filter_by(question_id=question_id).first()
            if not question:
                logging.error(f"Question ID:{question_id} not exist")
                return {"error": "Question not exist"}, 404

            quiz.questions.append(question)
            db.session.flush()
            db.session.commit()
            logging.info(f"Question {question_id} added to Quiz {quiz_id}")
            return {"message": f"Question {question_id} added to quiz {quiz_id} successfully."}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Database error occurred: {str(e)}")
            return {"error": "Database error occurred"}, e.code
        except Exception as e:
            if isinstance(e, HTTPException):
                logging.error(f"HTTP error occurred: {str(e)}")
                return {"error": "HTTP error occurred"}, e.code
            else:
                db.session.rollback()
                logging.error(f"Unexpected error occurred: {str(e)}")
                return {"error": "Unexpected error occurred"}, e.code

    def delete(self):
        try:
            args = quiz_question_template.parse_args()
            quiz_id = args.get("quiz_id")
            question_id = args.get("question_id")

            quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
            if not quiz:
                logging.error(f"Quiz ID:{args.get('quiz_id')} not exist")
                return {"error": "quiz not exist"}, 404

            question = Question.query.filter_by(question_id=question_id).first()
            if not question:
                logging.error(f"Question ID:{question_id} not exist")
                return {"error": "Question not exist"}, 404

            quiz.questions.remove(question)
            db.session.flush()
            db.session.commit()
            logging.info(f"Question {question_id} deleted from Quiz {quiz_id}")
            return {"message": f"Question {question_id} deleted from quiz {quiz_id} successfully."}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Database error occurred: {str(e)}")
            return {"error": "Database error occurred"}, e.code
        except Exception as e:
            if isinstance(e, HTTPException):
                logging.error(f"HTTP error occurred: {str(e)}")
                return {"error": "HTTP error occurred"}, e.code
            else:
                db.session.rollback()
                logging.error(f"Unexpected error occurred: {str(e)}")
                return {"error": "Unexpected error occurred"}, e.code

quiz_user_template = reqparse.RequestParser()
quiz_user_template.add_argument("quiz_id", type=int, required=False)
quiz_user_template.add_argument("user_id", type=str, required=False)


class QuizesUsersRoute(ProtectedResource):
    def post(self):
        try:
            args = quiz_user_template.parse_args()
            quiz_id = args.get("quiz_id")
            user_id = args.get("user_id")

            quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
            if not quiz:
                logging.error(f"Quiz ID:{args.get('quiz_id')} not exist")
                return {"error": "quiz not exist"}, 404

            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                logging.error(f"user ID:{user_id} not exist")
                return {"error": "user not exist"}, 404

            quiz.users.append(user)
            db.session.flush()
            db.session.commit()
            logging.info(f"user {user_id} added to Quiz {quiz_id}")
            return {"message": f"user {user_id} added to Quiz {quiz_id} successfully."}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Database error occurred: {str(e)}")
            return {"error": "Database error occurred"}, e.code
        except Exception as e:
            if isinstance(e, HTTPException):
                logging.error(f"HTTP error occurred: {str(e)}")
                return {"error": "HTTP error occurred"}, e.code
            else:
                db.session.rollback()
                logging.error(f"Unexpected error occurred: {str(e)}")
                return {"error": "Unexpected error occurred"}, e.code

    def delete(self):
        try:
            args = quiz_user_template.parse_args()
            quiz_id = args.get("quiz_id")
            user_id = args.get("user_id")

            quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
            if not quiz:
                logging.error(f"Quiz ID:{args.get('quiz_id')} not exist")
                return {"error": "quiz not exist"}, 404

            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                logging.error(f"user ID:{user_id} not exist")
                return {"error": "user not exist"}, 404

            quiz.users.remove(user)
            db.session.flush()
            db.session.commit()
            logging.info(f"user {user_id} deleted from Quiz {quiz_id}")
            return {"message": f"user {user_id} deleted from Quiz {quiz_id} successfully."}, 200
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f"Database error occurred: {str(e)}")
            return {"error": "Database error occurred"}, e.code
        except Exception as e:
            if isinstance(e, HTTPException):
                logging.error(f"HTTP error occurred: {str(e)}")
                return {"error": "HTTP error occurred"}, e.code
            else:
                db.session.rollback()
                logging.error(f"Unexpected error occurred: {str(e)}")
                return {"error": "Unexpected error occurred"}, e.code
            
#############################################################
###################### Utilities ######################
#############################################################

#############################################################
############# Get/Add/Update/Delete users ###################
#############################################################
user_create_template = reqparse.RequestParser()
user_create_template.add_argument("user_id", type=str, required=True)
user_create_template.add_argument("password", type=str, required=True)
user_create_template.add_argument("user_fname", type=str)
user_create_template.add_argument("user_lname", type=str)
user_create_template.add_argument("role_id", type=str, required=True)
user_create_template.add_argument("user_qualification", type=str)
user_create_template.add_argument("user_dob", type=date_type)

user_update_template = reqparse.RequestParser()
user_update_template.add_argument("user_id", type=str, required=True)
user_update_template.add_argument("password", type=str)
user_update_template.add_argument("user_fname", type=str)
user_update_template.add_argument("user_lname", type=str)
user_update_template.add_argument("role_id", type=str)
user_update_template.add_argument("user_qualification", type=str)
user_update_template.add_argument("user_dob", type=date_type)

option_fields = {
    "option_id": fields.String,
    "option_statement": fields.String,
    "option_key": fields.String,
    "question_id": fields.String,
}

question_fields = {
    "question_id": fields.String,
    "question_statement": fields.String,
    "chapter_id": fields.String,
    "options": fields.Nested(option_fields),
}

quiz_fields = {
    "quiz_id": fields.Integer,
    "quiz_title": fields.String,
    "date": fields.String,
    "duration": fields.String,
    "subject_id": fields.String,
    "questions": fields.Nested(question_fields),
}

response_fields = {
    "response_id": fields.Integer,
    "user_id": fields.String,
    "quiz_id": fields.Integer,
    "question_id": fields.Integer,
    "option_id": fields.Integer,
    "score": fields.Integer,
    "time": fields.String,
    "attempt": fields.Integer,
}

user_fields = {
    "user_id": fields.String,
    "last_login": fields.String,
    "user_fname": fields.String,
    "user_lname": fields.String,
    "user_qualification": fields.String,
    "user_dob": fields.String,   # date formatted as string
    "role_id": fields.String,
}


class UserRoute(ProtectedResource):
    def get(self, user_id=None):
        return global_read(User, user_fields, "user_id", user_id)

    def post(self):
        return global_create(User, user_create_template.parse_args(), "user_id", self)
        

    def patch(self):
        return global_update(User, user_update_template.parse_args(), "user_id", self)
        

    def delete(self, user_id):
        return global_delete(User, "user_id", user_id)
    
#############################################################
############# Get/Add/Update/Delete users ###################
#############################################################

#############################################################
################### Get/Add/Delete roles ####################
#############################################################
roles_create_template = reqparse.RequestParser()
roles_create_template.add_argument("role_id", type=str, required=True)
roles_create_template.add_argument("role_description", type=str)

roles_update_template = reqparse.RequestParser()
roles_update_template.add_argument("role_id", type=str, required=True)
roles_update_template.add_argument("role_description", type=str)

roles_fields = {
    "role_id": fields.String,
    "role_description": fields.String
}

class RolesRoute(ProtectedResource):
    def get(self, role_id=None):
        return global_read(Role, roles_fields, "role_id", role_id)

    def post(self):
        return global_create(Role, roles_create_template.parse_args(), "role_id", self)

    def patch(self):
        return global_update(Role, roles_update_template.parse_args(), "role_id", self)

    def delete(self, role_id):
        return global_delete(Role, "role_id", role_id)
    
#############################################################
################### Get/Add/Delete roles ####################
#############################################################

#############################################################
###################### Get/Add/Delete Subject ##############
#############################################################
subject_create_template = reqparse.RequestParser()
subject_create_template.add_argument("subject_name", type=str, required=True)
subject_create_template.add_argument("subject_description", type=str)

subject_update_template = reqparse.RequestParser()
subject_update_template.add_argument("subject_id", type=int, required=True)
subject_update_template.add_argument("subject_name", type=str)
subject_update_template.add_argument("subject_description", type=str)

chapter_fields = {
    "chapter_id": fields.Integer,
    "chapter_name": fields.String,
    "chapter_description": fields.String,
    "questions": fields.Nested(question_fields),
}

subject_fields = {
    "subject_id": fields.Integer,
    "subject_name": fields.String,
    "subject_description": fields.String,
    "chapters": fields.Nested(chapter_fields),
}

class SubjectsRoute(ProtectedResource):
    def get(self, subject_id=None):
        return global_read(Subject, subject_fields, "subject_id", subject_id)

    def post(self):
        return global_create(Subject, subject_create_template.parse_args(), "subject_id", self)

    def patch(self):
        return global_update(Subject, subject_update_template.parse_args(), "subject_id", self)

    def delete(self, subject_id):
        return global_delete(Subject, "subject_id", subject_id)

#############################################################
###################### Get/Add/Delete Subject ##############
#############################################################


#############################################################
###################### Get/Add/Delete Chapter ##############
#############################################################
chapter_create_template = reqparse.RequestParser()
chapter_create_template.add_argument("chapter_name", type=str, required=True)
chapter_create_template.add_argument("chapter_description", type=str)
chapter_create_template.add_argument("subject_id", type=int, required=True)

chapter_update_template = reqparse.RequestParser()
chapter_update_template.add_argument("chapter_id", type=int, required=True)
chapter_update_template.add_argument("chapter_name", type=str)
chapter_update_template.add_argument("chapter_description", type=str)
chapter_update_template.add_argument("subject_id", type=int)


class ChaptersRoute(ProtectedResource):
    def get(self, chapter_id=None):
        return global_read(Chapter, chapter_fields, "chapter_id", chapter_id)

    def post(self):
        return global_create(Chapter, chapter_create_template.parse_args(), "chapter_id", self)

    def patch(self):
        return global_update(Chapter, chapter_update_template.parse_args(), "chapter_id", self)

    def delete(self, chapter_id):
        return global_delete(Chapter, "chapter_id", chapter_id)

#############################################################
###################### Get/Add/Delete Chapter ##############
#############################################################

#############################################################
###################### Get/Add/Delete Quizes ################
#############################################################
quiz_create_template = reqparse.RequestParser()
quiz_create_template.add_argument("quiz_title", type=str, required=True)
quiz_create_template.add_argument("date", type=date_type, required=True)
quiz_create_template.add_argument("duration", type=time_type, required=True)
quiz_create_template.add_argument("subject_id", type=int, required=True)

quiz_update_template = reqparse.RequestParser()
quiz_update_template.add_argument("quiz_id", type=int, required=True)
quiz_update_template.add_argument("quiz_title", type=str)
quiz_update_template.add_argument("date", type=date_type)
quiz_update_template.add_argument("duration", type=time_type)
quiz_update_template.add_argument("subject_id", type=int)

class QuizesRoute(ProtectedResource):
    def get(self, quiz_id=None):
        return global_read(Quiz, quiz_fields, "quiz_id", quiz_id)

    def post(self):
        return global_create(Quiz, quiz_create_template.parse_args(), "quiz_id", self)

    def patch(self):
        return global_update(Quiz, quiz_update_template.parse_args(), "quiz_id", self)

    def delete(self, quiz_id):
        return global_delete(Quiz, "quiz_id", quiz_id)

#############################################################
###################### Get/Add/Delete Quizes ################
#############################################################

############################################################
###################### Get/Add/Delete questions ################
#############################################################

question_create_template = reqparse.RequestParser()
question_create_template.add_argument("question_statement", type=str, required=True)
question_create_template.add_argument("chapter_id", type=int, required=True)

question_update_template = reqparse.RequestParser()
question_update_template.add_argument("question_id", type=int, required=True)
question_update_template.add_argument("question_statement", type=str)
question_update_template.add_argument("chapter_id", type=int)


class QuestionsRoute(ProtectedResource):
    def get(self, question_id=None):
        return global_read(Question, question_fields, "question_id", question_id)

    def post(self):
        return global_create(Question, question_create_template.parse_args(), "question_id", self)

    def patch(self):
        return global_update(Question, question_update_template.parse_args(), "question_id", self)

    def delete(self, question_id):
        return global_delete(Question, "question_id", question_id)

#############################################################
################## Get/Add/Delete questiones ################
#############################################################


################################################################
#################### Get/Add/Delete options ####################
################################################################
option_create_template = reqparse.RequestParser()
option_create_template.add_argument("option_statement", type=str, required=True)
option_create_template.add_argument("option_key", type=bool, required=True)
option_create_template.add_argument("question_id", type=int, required=True)

option_update_template = reqparse.RequestParser()
option_update_template.add_argument("option_id", type=int, required=True)
option_update_template.add_argument("option_statement", type=str)
option_update_template.add_argument("option_key", type=bool)
option_update_template.add_argument("question_id", type=int)


class OptionsRoute(ProtectedResource):
    def get(self, option_id=None):
        return global_read(Option, option_fields, "option_id", option_id)

    def post(self):
        return global_create(Option, option_create_template.parse_args(), "option_id", self)

    def patch(self):
        return global_update(Option, option_update_template.parse_args(), "option_id", self)

    def delete(self, option_id):
        return global_delete(Option, "option_id", option_id)

#############################################################
################## Get/Add/Delete optiones ################
#############################################################

############################################################
###################### Get/Add/Delete response ################
#############################################################
response_create_template = reqparse.RequestParser()
response_create_template.add_argument("user_id", type=str, required=True)
response_create_template.add_argument("quiz_id", type=int, required=True)
response_create_template.add_argument("question_id", type=int, required=True)
response_create_template.add_argument("option_id", type=int, required=True)
response_create_template.add_argument("score", type=int, required=True)
response_create_template.add_argument("time", type=datetime_type, required=True)
response_create_template.add_argument("attempt", type=int, required=True)

response_update_template = reqparse.RequestParser()
response_update_template.add_argument("response_id", type=int, required=True)
response_update_template.add_argument("user_id", type=str)
response_update_template.add_argument("quiz_id", type=int)
response_update_template.add_argument("question_id", type=int)
response_update_template.add_argument("option_id", type=int)
response_update_template.add_argument("score", type=int)
response_update_template.add_argument("time", type=datetime_type)
response_update_template.add_argument("attempt", type=int)


class ResponseRoute(ProtectedResource):
    def get(self, response_id=None):
        return global_read(Response, response_fields, "response_id", response_id)

    def post(self):
        return global_create(Response, response_create_template.parse_args(), "response_id", self)

    def patch(self):
        return global_update(Response, response_update_template.parse_args(), "response_id", self)

    def delete(self, response_id):
        return global_delete(Response, "response_id", response_id)

#############################################################
###################### Get/Add/Delete response ################
#############################################################


############################################################
###################### Get/Add/Delete quizquestions ################
#############################################################



#############################################################
################## Get/Add/Delete quizquestiones ################
#############################################################

############################################################
###################### Get/Add/Delete quizusers ################
#############################################################



#############################################################
################## Get/Add/Delete quizuseres ################
#############################################################

############################################################
###################### Get Score ################
#############################################################
score_template = reqparse.RequestParser()
score_template.add_argument("user_id", type=str, required=False)
score_template.add_argument("quiz_id", type=str, required=False)
score_template.add_argument("score", type=str, required=False)
score_template.add_argument("attempt", type=str, required=False)

score_fields = {
    "user_id": fields.Integer,
    "quiz_id": fields.Integer,
    "attempt": fields.Integer,
    "total_score": fields.Integer
}

class ScoreRoute(Resource):
    @marshal_with(score_fields)
    def get(self):
        try:
            results = (
                db.session.query(
                    Response.user_id,
                    Response.quiz_id,
                    Response.attempt,
                    func.sum(Response.score).label("total_score")
                )
                .group_by(Response.user_id, Response.quiz_id, Response.attempt)
                .all()
            )
            
            if not results:
                logging.error(f"Score not found")
                return {"error": "Score not found"}, 404
            return results
        except SQLAlchemyError as e:
            logging.error(f"Database error occurred: {str(e)}")
            return {"error": "Database error occurred"}, e.code
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")
            return {"error": "Unexpected error occurred"}, e.code
        
    @marshal_with(score_fields)
    def post(self):
        try:
            args = score_template.parse_args()
            user_id = args.get("user_id")
            quiz_id = args.get("quiz_id")
            attempt = args.get("attempt")
            results = None
            if user_id and quiz_id and attempt:
                results = (
                    db.session.query(
                        Response.user_id,
                        Response.quiz_id,
                        Response.attempt,
                        func.sum(Response.score).label("total_score")
                    )
                    .filter(
                        Response.user_id == user_id,
                        Response.quiz_id == quiz_id,
                        Response.attempt == attempt
                    )
                    .group_by(Response.user_id, Response.quiz_id, Response.attempt)
                    .all()
                )
            if not results:
                logging.error(f"Score not found")
                return {"error": "Score not found"}, 404
            return results
        except SQLAlchemyError as e:
            logging.error(f"Database error occurred: {str(e)}")
            return {"error": "Database error occurred"}, e.code
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")
            return {"error": "Unexpected error occurred"}, e.code