class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///quizmaster.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    JWT_SECRET_KEY = "123456"  # Change this to a random secret key
