from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from modules import db,bcrypt,jwt_denylist,Config,SetupDB,UserRoute,LoginRoute,LoginRefreshRoute,LoginPingRoute,LogoutRoute,RegisterRoute,RolesRoute,SubjectsRoute,ChaptersRoute, QuizesRoute,QuestionsRoute,OptionsRoute,ResponseRoute,QuizesQuestionsRoute,QuizesUsersRoute

app = Flask(__name__)
app.config.from_object(Config)
CORS(app,supports_credentials=True)


db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def check_if_token_in_denylist(_, jwt_payload):
    jti = jwt_payload["jti"]  # Unique identifier for the JWT
    return jti in jwt_denylist

@jwt.revoked_token_loader
def revoked_token_callback(_, __):
    return {"error": "Token has been revoked"}, 401

api = Api(app)

with app.app_context():
    SetupDB()

api.add_resource(UserRoute, '/api/users', '/api/users/<string:user_id>')
api.add_resource(RolesRoute, '/api/roles', '/api/roles/<string:role_id>')
api.add_resource(SubjectsRoute, '/api/subjects', '/api/subjects/<string:subject_id>')
api.add_resource(ChaptersRoute, '/api/chapters', '/api/chapters/<string:chapter_id>')
api.add_resource(QuizesRoute, '/api/quizzes', '/api/quizzes/<string:quiz_id>')
api.add_resource(QuestionsRoute, '/api/questions', '/api/questions/<string:question_id>')
api.add_resource(OptionsRoute, '/api/options', '/api/options/<string:option_id>')
api.add_resource(ResponseRoute, '/api/responses', '/api/responses/<string:response_id>')

api.add_resource(RegisterRoute, '/api/users/register')
api.add_resource(LoginRoute, '/api/users/login')
api.add_resource(LoginPingRoute, '/api/users/login/ping')
api.add_resource(LogoutRoute, '/api/users/logout')
api.add_resource(LoginRefreshRoute, '/api/users/login/refresh')
api.add_resource(QuizesQuestionsRoute, '/api/quizzes/questions')
api.add_resource(QuizesUsersRoute, '/api/quizzes/users')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)