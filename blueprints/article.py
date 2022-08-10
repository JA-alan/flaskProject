import json
import uuid
import os
from flask import Blueprint, render_template, redirect, flash, request, g, url_for, Response
import global_setting
from .forms import ArticleForm
from models import ArticleModel, AnswerModel
from decorators import login_required
from exts import db
from sqlalchemy import or_
from datetime import datetime

bp = Blueprint("article", __name__, url_prefix="/")
ALLOWED_EXT = ['png', 'jpg', 'jpeg']
UPLOAD_DIR = './static/photo'


@bp.route("/user/article", methods=["GET", "POST"])  # 文章主页
def user_article():
    if request.method == "GET":
        articles = ArticleModel.query.order_by(ArticleModel.create_time.desc()).all()
        return render_template("article.html", articles=articles)
    else:
        articles = ArticleModel.query.filter_by(ArticleModel.article_id).all()
        return render_template("article.html", articles=articles)


def save_to_local(file, file_name):  # 保存文件
    save_dir = UPLOAD_DIR
    file.save(os.path.join(save_dir, file_name))
    return file_name


@bp.route("auth/user/article", methods=["GET", "POST"])  # 文章主页
def auth_user_article():
    articl_dict = []
    if request.method == "GET":
        articles = ArticleModel.query.order_by(ArticleModel.browse_number.desc())
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


@bp.route("/user/post/article", methods=["GET", "POST"])  # 发布文章
@login_required
def user_post_article():
    if request.method == "GET":
        return render_template("post_article.html")
    elif request.method == "POST":
        file = request.files['file']
        form = ArticleForm(request.form)
        if form.validate():
            article_id = "A" + global_setting.inset_token().upper()
            title = form.title.data
            head = form.head.data
            content = form.content.data
            if file.filename == '':
                url = 'null.png'
                browse_number = 1
                cont = ArticleModel(browse_number=browse_number, title=title, head=head, content=content,
                                    author=g.user,
                                    article_id=article_id, Photo=url)
                db.session.add(cont)
                db.session.commit()
                return redirect("/")
            else:
                file_ext = ''
                if file.filename.find('.') > 0:
                    file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
                if file_ext in ALLOWED_EXT:
                    file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
                    # 保存到本地
                    url = save_to_local(file, file_name)
                    cont = ArticleModel(title=title, head=head, content=content, author=g.user,
                                        article_id=article_id, Photo=url)
                    db.session.add(cont)
                    db.session.commit()
                    return redirect("/")
                else:
                    flash("标题或内容格式错误")
                    return redirect(url_for("qa.user_post_article"))

        else:
            return global_setting.server_error()


@bp.route("/article/detail/<int:article_id>", methods=["GET", "POST"])  # 文章详情
@login_required
def article_detail(article_id):
    if request.method == "GET":
        answer = AnswerModel.query.filter_by(content_type=1).first()
        article = ArticleModel.query.get(article_id)
        model_list = ArticleModel.query.filter_by(id=article_id).first()
        num = model_list.browse_number
        num = num + 1
        article.browse_number = num
        db.session.commit()
        return render_template("article_detail.html", article=article, answer=answer)

    elif request.method == "POST":
        content = request.form["content"]
        if content is None:
            flash("请输入评论")
            return redirect(url_for("article.article_detail", function_id=article_id))
        else:
            answer_id = "AN" + global_setting.inset_token().upper()
            content_type = 1
            answer_model = AnswerModel(answer_content=content, author=g.user, article_id=article_id,
                                       answer_id=answer_id, content_type=content_type)
            db.session.add(answer_model)
            db.session.commit()
            return redirect(url_for("article.article_detail", article_id=article_id))
    else:
        flash("请求格式错误")
        return redirect(url_for("article.article_detail", article_id=article_id))


@bp.route("/new/article")
def new_article():
    articles = ArticleModel.query.order_by(ArticleModel.create_time.desc()).all()
    return render_template("articles.html", articles=articles)


@bp.route("/del/user/article", methods=["POST", "GET"])
@login_required
def del_user_article():
    if request.method == "GET":
        flash("请求错误")
        return redirect("article.del_user_article")
    else:
        form = ArticleForm(request.form)
