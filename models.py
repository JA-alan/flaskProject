from exts import db
from datetime import datetime


class User_Model(db.Model):
    """用户表"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, unique=True)
    user = db.Column(db.String(200), nullable=True, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=False, unique=False)
    gender = db.Column(db.String(100), nullable=False, unique=False)
    character = db.Column(db.String(100), nullable=False, unique=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=True)
    hash_password = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.Integer, nullable=True, unique=True)
    portrait = db.Column(db.String(200), nullable=True, unique=False)
    user_type = db.Column(db.Integer, nullable=True)
    token = db.Column(db.String(50), nullable=True, unique=True)
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now())


class Email_Captcha_Model(db.Model):
    """验证码"""
    __tablename__ = "email_captcha"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String(40), nullable=True, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    captcha = db.Column(db.String(10), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    author = db.relationship(User_Model, backref="captcha")


class ArticleModel(db.Model):
    """文章表"""
    __tablename__ = "user_article"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.String(200), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=True, unique=False)
    head = db.Column(db.String(200), nullable=True, unique=False)
    content = db.Column(db.TEXT, nullable=False)
    label_id = db.Column(db.Integer, nullable=True, unique=False)
    browse_number = db.Column(db.Integer, nullable=True, unique=False)
    likes_number = db.Column(db.Integer, nullable=True, unique=False)
    collection_number = db.Column(db.Integer, nullable=True, unique=False)
    Photo = db.Column(db.String(200), nullable=True, unique=False)
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    author = db.relationship(User_Model, backref="articles")


class FunctionModel(db.Model):
    """问答表"""
    __tablename__ = "user_function"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    function_id = db.Column(db.String(200), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=True, unique=False)
    content = db.Column(db.TEXT, nullable=False)
    label_id = db.Column(db.Integer, nullable=True, unique=False)
    browse_number = db.Column(db.Integer, nullable=True, unique=False)
    likes_number = db.Column(db.Integer, nullable=True, unique=False)
    collection_number = db.Column(db.Integer, nullable=True, unique=False)
    Photo = db.Column(db.String(200), nullable=True, unique=False)
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    author = db.relationship(User_Model, backref="functions")


class AnswerModel(db.Model):
    """文章评论/问答表"""
    __tablename__ = "user_answer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    answer_id = db.Column(db.String(200), nullable=False, unique=True)
    content_type = db.Column(db.Integer, nullable=True, unique=False)
    answer_content = db.Column(db.TEXT, nullable=False)
    likes_number = db.Column(db.Integer, nullable=True, unique=False)
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    function_id = db.Column(db.Integer, db.ForeignKey("user_function.id"))
    article_id = db.Column(db.Integer, db.ForeignKey("user_article.id"))

    function = db.relationship(FunctionModel, backref=db.backref("answers",order_by=create_time.desc()))
    article = db.relationship(ArticleModel, backref=db.backref("answers",order_by=create_time.desc()))

    author = db.relationship(User_Model, backref="answers")


class Developer_Diary_Model(db.Model):
    """开发者日记表"""
    __tablename__ = "developer_diary"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diary_id = db.Column(db.String(200), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=True, unique=False)
    type = db.Column(db.Integer, nullable=True, unique=False)
    content = db.Column(db.TEXT, nullable=False)
    Photo = db.Column(db.String(200), nullable=True, unique=False)
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    author = db.relationship(User_Model, backref="diarys")


class Root_Diary_Model(db.Model):
    """留言表"""
    __tablename__ = "root_diary"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    root_id = db.Column(db.String(200), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=True, unique=False)
    content = db.Column(db.TEXT, nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.now())
    update_time = db.Column(db.DateTime, default=datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    author = db.relationship(User_Model, backref="roots")
