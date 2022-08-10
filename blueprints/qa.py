import json
from flask import Blueprint, render_template, redirect, flash, request, g, url_for, Response
import global_setting
from .forms import QAFunctionForm
from models import ArticleModel, FunctionModel, AnswerModel
from decorators import login_required
from exts import db
from sqlalchemy import or_
from datetime import datetime

bp = Blueprint("qa", __name__, url_prefix="/")
ALLOWED_EXT = ['png', 'jpg', 'jpeg']
UPLOAD_DIR = './static/photo'


@bp.route("/")  # 首页
def index():
    #  按照时间倒叙排序
    # articles = ArticleModel.query.order_by(ArticleModel.text("-create_time")).all()
    articles = ArticleModel.query.order_by(ArticleModel.browse_number.desc())[0:3]
    functions = FunctionModel.query.order_by(FunctionModel.browse_number.desc())[0:1]
    f = dayofweek()
    return render_template("index.html", articles=articles, functions=functions, f=f)


@bp.route("get/index/article", methods=["GET", "POST"])
def get_index_article():
    articl_dict = []
    if request.method == "GET":
        articles = ArticleModel.query.order_by(ArticleModel.browse_number.desc())[0:3]

        for article in articles:
            article_dict = {
                "article_id": article.article_id,
                "title": article.title,
                "head": article.head,
                "content": article.content,
                "browse_number": article.browse_number,
                "likes_number": article.likes_number,
                "collection_number": article.collection_number,
                "photo": article.Photo,
                "create_time": article.create_time
            }
            articl_dict.append(article_dict)
        return Response(json.dumps({"code": 200, "msg": "操作成功", "data": articl_dict}, default=str),
                        mimetype='application/json')
    elif request.method == "POST":
        return global_setting.good_message()


@bp.route("get/index/qa_function", methods=["GET", "POST"])
def get_index_qa_function():
    articl_dict = []
    if request.method == "GET":
        articles = FunctionModel.query.order_by(FunctionModel.browse_number.desc())[0:1]
        for article in articles:
            article_dict = {
                "article_id": article.function_id,
                "title": article.title,
                "content": article.content,
                "browse_number": article.browse_number,
                "likes_number": article.likes_number,
                "collection_number": article.collection_number,
                "photo": article.Photo,
                "create_time": article.create_time
            }
            articl_dict.append(article_dict)
        return Response(json.dumps({"code": 200, "msg": "操作成功", "data": articl_dict}, default=str),
                        mimetype='application/json')


def dayofweek():  # 判断今天星期几
    dayOfWeek = datetime.now().weekday()
    dayOfWeek = dayOfWeek + 1
    if dayOfWeek == 1:
        f = open('static/photo/day1-1.jpeg')
        return f
    elif dayOfWeek == 2:
        f = open('static/photo/day2-1.jpeg')
        return f
    elif dayOfWeek == 3:
        f = open('static/photo/day3.jpeg')
        return f
    elif dayOfWeek == 4:
        f = open('static/photo/day4.png')
        return f
    elif dayOfWeek == 5:
        f = open('static/photo/day5.jpeg')
        return f
    elif dayOfWeek == 6:
        f = open('static/photo/day6.jpeg')
        return f
    elif dayOfWeek == 7:
        f = open('static/photo/day7.png')
        return f
    else:
        return global_setting.server_error()


@bp.route("/question/public")  # 你问我答主页
def public_question():
    return render_template("public_question.html")


@bp.route("/qa_function/homepage", methods=["GET", "POST"])  # 问答主页
def qa_function_homepage():
    if request.method == "GET":
        functions = FunctionModel.query.order_by(FunctionModel.create_time.desc()).all()
        return render_template("qa_function.html", functions=functions)


@bp.route("auth/user/qa_function", methods=["GET", "POST"])
def auth_user_qa_function():
    articl_dict = []
    if request.method == "GET":
        articles = FunctionModel.query.order_by(FunctionModel.browse_number.desc())
        for qa in articles:
            article_dict = {
                "article_id": qa.function_id,
                "title": qa.title,
                "content": qa.content,
                "browse_number": qa.browse_number,
                "likes_number": qa.likes_number,
                "collection_number": qa.collection_number,
                "photo": qa.Photo,
                "create_time": qa.create_time
            }
            articl_dict.append(article_dict)
        return Response(json.dumps({"code": 200, "msg": "操作成功", "data": articl_dict}, default=str),
                        mimetype='application/json')


@bp.route("user/post/qa_function", methods=["GET", "POST"])  # 发布问答
@login_required
def user_post_qa_function():
    if request.method == "GET":
        return render_template("post_qa_function.html")
    elif request.method == "POST":
        form = QAFunctionForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            function_id = "QA" + global_setting.inset_token().upper()
            browse_number = 1
            cont = FunctionModel(browse_number=browse_number, function_id=function_id, title=title, content=content,
                                 author=g.user)
            db.session.add(cont)
            db.session.commit()
            return redirect(url_for("qa.qa_function_homepage"))
        else:
            flash("标题或内容格式错误")
            return redirect(url_for("qa.user_post_qa_function"))

    else:
        return global_setting.server_error()


@bp.route("/qa_function/detail/<int:function_id>", methods=["GET", "POST"])  # 问答详情
@login_required
def qa_function_detail(function_id):
    if request.method == "GET":
        function = FunctionModel.query.get(function_id)
        answer = AnswerModel.query.filter_by(content_type=2).all()
        num = function.browse_number
        num = num + 1
        function.browse_number = num
        db.session.commit()
        return render_template("qafunction_detail.html", function=function, answer=answer)


@bp.route("post/answer/<int:function_id>", methods=["GET", "POST"])  # 发布问答评论
@login_required
def post_answer(function_id):
    if request.method == "POST":
        content = request.form["content"]
        if content is None:
            flash("请输入评论")
            return redirect(url_for("qa.qa_function_detail", function_id=function_id))
        else:
            answer_id = "AN" + global_setting.inset_token().upper()
            content_type = 2
            answer_model = AnswerModel(answer_content=content, author=g.user, function_id=function_id,
                                       answer_id=answer_id, content_type=content_type)
            db.session.add(answer_model)
            db.session.commit()
            return redirect(url_for("qa.qa_function_detail", function_id=function_id))
    else:
        flash("表单验证失败")
        return redirect(url_for("qa.qa_function_detail", function_id=function_id))


@bp.route("user/search")  # 搜索
def user_search():
    q = request.args.get("query")
    functions = FunctionModel.query.filter(
        or_(FunctionModel.title.contains(q), FunctionModel.content.contains(q))).order_by(db.text("-create_time")).all()
    articles = ArticleModel.query.filter(
        or_(ArticleModel.title.contains(q), ArticleModel.content.contains(q), ArticleModel.head.contains(q))).order_by(
        db.text("-create_time")).all()
    return render_template("public_question.html", functions=functions, articles=articles)


@bp.route("user/message")  # 消息
def user_message():
    if request.method == "GET":
        return render_template("user_message.html")
    else:
        return global_setting.good_message()
