import uuid
import os
import global_setting
from models import ArticleModel
from flask import Flask, session, g, request, redirect
from flask_migrate import Migrate
import config
from exts import db, mail
from blueprints import qa_bp, user_bp, article_bp
from models import User_Model
from config import BASE_URL_TEST, PHOTO_PATH, BASE_URL_DEV
import email_validator
from log.web_logs import init_logging

app = Flask(__name__)
app.config.from_object(config)
app.debug = True
app.config["JSON_AS_ASCII"] = False
app.config['JSON_SORT_KEYS'] = False
app.config["SECRET_KEY"] = 'TPmi4aLWRbyVq8zu9v82dWYW1'
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"
db.init_app(app)
mail.init_app(app)
# 设置允许上传的文件格式
app.config['ALLOWED_EXT'] = ['png', 'jpg', 'jpeg']
app.config['UPLOAD_DIR'] = './static/photo'

# 设置图片压缩尺寸
image_c = 1000

migrate = Migrate(app, db)

app.register_blueprint(qa_bp)
app.register_blueprint(user_bp)
app.register_blueprint(article_bp)


@app.before_request  # 获取用户信息作为全局变量
def before_request():
    user_id = session.get("user_id")
    if user_id:
        try:
            user = User_Model.query.get(user_id)
            #  setattr(g, "user", user)
            g.user = user
        except:
            g.user = None


# 请求来了 -> before -> 视图函数 -> 视图函数中返回模板 -> context


@app.context_processor
def context_processor():
    if hasattr(g, "user"):
        return {"user": g.user}
    else:
        return {}


# init_logging()
if __name__ == '__main__':
    app.run()
