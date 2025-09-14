from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()
jwt_denylist = set()

######################################################
################### User Management ##################
######################################################
class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    user_password = db.Column(db.String, unique=False, nullable=False, default=lambda: bcrypt.generate_password_hash("nopassword").decode("utf-8"))
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_fname = db.Column(db.String, unique=False, nullable=True)  # First name
    user_lname = db.Column(db.String, unique=False, nullable=True)  # Last name
    user_qualification = db.Column(db.String, unique=False, nullable=True)  # Qualification
    user_dob = db.Column(db.Date, unique=False, nullable=True)  # Date of birth
    # Foreign key linking to the Role table
    role_id = db.Column(db.Integer, db.ForeignKey("role.role_id"), nullable=False)
    # Many-to-one relationship with the Role table
    role = db.relationship("Role", back_populates="users", lazy=True)
    # One-to-many relationship with the Response table
    response = db.relationship(
        "Response", back_populates="user", uselist=True, lazy=True, cascade="all, delete-orphan"
    )
    # Many-to-many relationship with the Quiz table
    quizzes = db.relationship(
        "Quiz", secondary="quiz_user_association", back_populates="users", lazy=True
    )

    def __init__(self, user_id, password = "nopassword", role_id = None, user_fname = None, user_lname = None, user_qualification = None, user_dob = None):
        self.user_id = user_id
        self.password = password
        self.user_fname = user_fname
        self.user_lname = user_lname
        self.user_qualification = user_qualification
        self.user_dob = user_dob
        self.role_id = role_id


    # write-only password property
    @property
    def password(self):
        raise AttributeError("Password is write-only")
    
    @password.setter
    def password(self, raw_password: str):
        if raw_password is None:
            raise ValueError("Password cannot be None")
        self.user_password = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def validate_password(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self.user_password, raw_password)


class Role(db.Model):
    __tablename__ = "role"
    role_id = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    role_description = db.Column(db.String, unique=False, nullable=True)  # Description
    # Back-populated one-to-many relationship with the User table
    users = db.relationship("User", back_populates="role", lazy=True)


######################################################
################# Syllabus Management ################
######################################################
class Subject(db.Model):
    __tablename__ = "subject"
    subject_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    subject_name = db.Column(db.String, unique=False, nullable=False)  # Subject name
    subject_description = db.Column(db.String, unique=False, nullable=True)  # Description
    # Back-populated one-to-many relationship with the Chapter table
    chapters = db.relationship("Chapter", back_populates="subject", lazy=True, cascade="all, delete-orphan")
    # Back-populated one-to-many relationship with the Quiz table
    quizzes = db.relationship("Quiz", back_populates="subject", lazy=True, cascade="all, delete-orphan")


class Chapter(db.Model):
    __tablename__ = "chapter"
    chapter_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    chapter_name = db.Column(db.String, unique=True, nullable=False)  # Chapter name
    chapter_description = db.Column(db.String, unique=False, nullable=True)  # Description
    # Foreign key linking to the Subject table
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.subject_id"), nullable=False)
    # Many-to-one relationship with the Subject table
    subject = db.relationship("Subject", back_populates="chapters", lazy=True)
    # Back-populated one-to-many relationship with the Question table
    questions = db.relationship("Question", back_populates="chapter", lazy=True, cascade="all, delete-orphan")


######################################################
############### Evaluation Management ################
######################################################
class Quiz(db.Model):
    __tablename__ = "quiz"
    quiz_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    quiz_title = db.Column(db.String, unique=False, nullable=False)  # Quiz title
    date = db.Column(db.Date, unique=False, nullable=False)  # Quiz date
    duration = db.Column(db.Time, unique=False, nullable=False)  # Quiz duration
    # Foreign key linking to the Subject table
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.subject_id"), nullable=False)
    # Many-to-one relationship with the Subject table
    subject = db.relationship("Subject", back_populates="quizzes", lazy=True)
    # Many-to-many relationship with the Question table
    questions = db.relationship("Question",secondary="quiz_question_association",back_populates="quizzes",lazy=True)
    # Many-to-many relationship with the User table
    users = db.relationship("User", secondary="quiz_user_association", back_populates="quizzes", lazy=True)
    # One-to-many relationship with the Response table
    response = db.relationship("Response", back_populates="quiz", uselist=True, lazy=True)


class QuizUserAssociation(db.Model):
    __tablename__ = "quiz_user_association"
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id"), primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.user_id"), primary_key=True)


class Response(db.Model):
    __tablename__ = "response"
    response_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    score = db.Column(db.Integer, unique=False, nullable=False)  # User's score
    time = db.Column(db.DateTime, unique=False, nullable=False)  # Response time
    attempt = db.Column(db.Integer, unique=False, nullable=False)  # Attempt number
    # Foreign key linking to the User table
    user_id = db.Column(db.String, db.ForeignKey("user.user_id"), nullable=False)
    # Foreign key linking to the Quiz table
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id"), nullable=False)
    # Foreign key linking to the Question table
    question_id = db.Column(db.Integer, db.ForeignKey("question.question_id"), nullable=False)
    # Foreign key linking to the Option table
    option_id = db.Column(db.Integer, db.ForeignKey("option.option_id"), nullable=False)
    user = db.relationship("User", back_populates="response", uselist=False, lazy=True)
    quiz = db.relationship("Quiz", back_populates="response", uselist=False, lazy=True)
    question = db.relationship("Question", back_populates="response", uselist=False, lazy=True)
    option = db.relationship("Option", back_populates="response", uselist=False, lazy=True)

    # Unique constraint to ensure a user can only respond to a quiz once per attempt
    __table_args__ = (UniqueConstraint("user_id", "quiz_id", "attempt","question_id","option_id", name="unique_response"),)


class QuizQuestionAssociation(db.Model):
    __tablename__ = "quiz_question_association"
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id"), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.question_id"), primary_key=True)


class Question(db.Model):
    __tablename__ = "question"
    question_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    question_statement = db.Column(db.String, unique=False, nullable=False)  # Statement
    # Foreign key linking to the Chapter table
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.chapter_id"), nullable=False)
    # Many-to-one relationship with the Chapter table
    chapter = db.relationship("Chapter", back_populates="questions", lazy=True)
    # Many-to-many relationship with the Quiz table
    quizzes = db.relationship("Quiz",secondary="quiz_question_association",back_populates="questions",lazy=True,)
    # One-to-many relationship with the Option table
    options = db.relationship("Option",back_populates="questions",uselist=True,lazy=True,cascade="all, delete-orphan",)
    # One-to-many relationship with the Response table
    response = db.relationship("Response", back_populates="question", lazy=True)


class Option(db.Model):
    __tablename__ = "option"
    option_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    option_statement = db.Column(db.String, unique=False, nullable=False)
    option_key = db.Column(db.Boolean, unique=False, nullable=False)
    # Foreign key linking to the Question table
    question_id = db.Column(db.Integer, db.ForeignKey("question.question_id"), nullable=False)
    # Relationships
    questions = db.relationship("Question", back_populates="options", uselist=False, lazy=True)
    response = db.relationship("Response", back_populates="option", uselist=True, lazy=True)
