import json
import os
from datetime import datetime
from flask import (Blueprint, render_template, request, url_for, redirect, g,
                   session, flash, Response)
from exts import mail, db
from flask_mail import Message
import string
import random
from models import Email_Captcha_Model, User_Model, Developer_Diary_Model, Root_Diary_Model, ArticleModel,\
    FunctionModel
import global_setting
from .forms import RegisterForm, LoginForm, Forgot_PasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import Email_Captcha

bp = Blueprint("user", __name__, url_prefix="/")


@bp.route("/login/index")
def login_index():
    return global_setting.good_message()


@bp.route("/login", methods=["GET", "POST"])  # 用户登录
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        form = LoginForm(request.form)
        if form.validate():
            user = form.user.data
            password = form.password.data
            user_model = User_Model.query.filter_by(user=user).first()
            if user_model:
                if user_model.hash_password is None:
                    flash("用户名或密码错误")
                    return render_template("login.html")
                elif check_password_hash(user_model.hash_password, password):
                    session["user_id"] = user_model.id
                    return redirect("/")
                else:
                    flash("用户名或密码错误")
                    return render_template("login.html")
            else:
                flash("用户名或密码错误")
                return render_template("login.html")
        else:
            flash("请求格式错误")
            return render_template("login.html")
    else:
        return global_setting.server_error()


@bp.route("/logout")  # 退出登录
def logout():
    session.clear()
    return redirect(url_for("qa.index"))


@bp.route("/register", methods=["GET", "POST"])  # 用户注册
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        form = RegisterForm(request.form)
        password = request.form["password"]
        psd_two = request.form["psd_two"]
        if psd_two != password:
            flash("两次密码不一致")
            return redirect(url_for("user.register"))
        if form.validate():
            email = form.email.data
            if email == User_Model.query.filter_by(email=email).first():
                flash("邮箱重复，请输入不同的邮箱")
                return redirect(url_for("user.register"))
            name = form.name.data
            user = form.user.data
            password = form.password.data

            user_list = User_Model.query.order_by(User_Model.user_id.desc()).first()
            user_id = user_list.user_id
            user_id = user_id + 1
            hash_password = generate_password_hash(password)
            gender = "性别未知，等待TA确认性别"
            character = "这个人很懒，还没有个性签名"
            user = User_Model(email=email, user=user, password=password, hash_password=hash_password, user_id=user_id,
                              name=name, character=character, gender=gender)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("user.login"))
        else:
            return redirect(url_for("user.register"))
            # return global_setting.server_error()
    else:
        flash("请求格式错误")
        return redirect(url_for("user.register"))


@bp.route('/send/mail/verification', methods=["GET", "POST"])  # 获取验证码
def send_email_verification_code():
    lettle = string.ascii_letters + string.digits
    captcha = "".join(random.sample(lettle, 4))
    if request.method == "GET":
        email = request.args.get("email")
        if email == '' or email is None:
            return global_setting.not_request_parameters()
        elif email:
            message = Message(subject="【安安的小屋】",
                              recipients=[email],
                              body=f"【安安的小屋】感谢您注册本网站,您的注册验证码是：{captcha},请勿告诉任何人哦")
            mail.send(message)
            captcha_moder = Email_Captcha_Model.query.filter_by(email=email).first()
            email_id = "E" + global_setting.inset_token().upper()
            if captcha_moder:
                captcha_moder.captcha = captcha
                captcha_moder.email = email
                db.session.commit()
                print("captcha:", captcha)
                return global_setting.good_message()

            else:
                captcha_moder = Email_Captcha_Model(email=email, captcha=captcha, email_id=email_id)
                db.session.add(captcha_moder)
                db.session.commit()
                print("captcha1:", captcha)
                return global_setting.good_message()
        else:
            return global_setting.good_message()
    elif request.method == "POST":
        email = request.form.get("email")
        if email == '' or email is None:
            return global_setting.not_request_parameters()

        elif email:
            captcha_moder = User_Model.query.filter_by(email=email).first()
            if captcha_moder:
                flash("邮箱重复")
                return {"code": 400, "msg": "邮箱已被注册"}
            else:
                Email_Captcha().email_code(email, captcha)
                return global_setting.good_message()
        else:
            return global_setting.lack_request_parameters()


@bp.route("/developer/diary", methods=["GET", "POST"])  # 开发者日记
def developer_diary():
    if request.method == "GET":
        diarys = Developer_Diary_Model.query.order_by(Developer_Diary_Model.create_time.desc()).all()
        return render_template("developer_diary.html", diarys=diarys)


@bp.route("post/developer/diary", methods=["GET", "POST"])  # 写日记,无页面
def post_developer_diary():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        type = request.form.get("type")
        if title is None or content is None:
            return global_setting.not_request_parameters()
        elif len(request.form) < 3 or len(request.form) > 3:
            return global_setting.lack_request_parameters()
        else:
            create_time = datetime.now()
            update_time = datetime.now()
            diary_id = "D" + global_setting.inset_token().upper()
            cont = Developer_Diary_Model(type=type, update_time=update_time, title=title, content=content,
                                         diary_id=diary_id, author_id=1, create_time=create_time)
            db.session.add(cont)
            db.session.commit()
            return global_setting.good_message()
    else:
        return global_setting.server_error()


@bp.route("contact/me", methods=["GET", "POST"])  # 留言
def contact_me():
    if request.method == "GET":
        root = Root_Diary_Model.query.order_by(Root_Diary_Model.create_time.desc()).all()
        return render_template("Contact_me.html", roots=root)

    elif request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        if content is None or content == "":
            flash("请填写内容")
            return redirect(url_for("user.contact_me"))

        else:
            root_id = "C" + global_setting.inset_token().upper()
            cont = Root_Diary_Model(root_id=root_id, author=g.user, title=title, content=content)
            db.session.add(cont)
            db.session.commit()
            return render_template("Contact_me.html")
    else:
        return global_setting.server_error()


@bp.route("space", methods=["GET", "POST"])
def user_space():
    if request.method == "GET":
        return render_template("user_space.html")


@bp.route("/set_session")
def set_session():
    session["username"] = "anan"
    return "设置成功"


@bp.route("/get_session")
def get_session():
    username = session.get("username")
    print(username)
    return "get session"


@bp.route("/get_bootstrap")
def get_bootstrap():
    username = session.get("username")
    print(username)
    return render_template("bj.html")


@bp.route("/forgot_password", methods=["GET", "POST"])  # 忘记密码
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.html")
    elif request.method == "POST":
        form = Forgot_PasswordForm(request.form)
        if form.validate():
            user = form.user.data
            password = form.password.data
            hash_password = generate_password_hash(password)
            usermodel = User_Model.query.filter_by(user=user).first()
            usermodel.password = password
            usermodel.hash_password = hash_password
            db.session.commit()
            return render_template("login.html")
        else:
            flash("")
            return render_template("forgot_password.html")
    else:
        flash("格式错误")
        return render_template("forgot_password.html")


@bp.route('/send/password/verification', methods=["GET", "POST"])  # 忘记密码获取验证码
def send_password_verification_code():
    lettle = string.ascii_letters + string.digits
    captcha = "".join(random.sample(lettle, 4))
    if request.method == "POST":
        email = request.form.get("email")
        if email == '' or email is None:
            return global_setting.not_request_parameters()

        else:
            Email_Captcha().email_code(email, captcha)
            return global_setting.good_message()
    else:
        return global_setting.lack_request_parameters()


@bp.route("/my", methods=["GET", "POST"])
def my():
    articl_dict = []
    if request.method == "GET":
        articles = ArticleModel.query.filter_by(author_id=g.user.id).all()
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


def save_to_local(file, file_name):  # 保存文件
    save_dir = "/static/js/fenye/article"
    file.save(os.path.join(save_dir, file_name))
    return file_name


@bp.route("/Myspace", methods=["GET", "POST"])
def My_space():
    my_portrait = User_Model.query.filter_by(user=g.user.user).first()
    f = open(my_portrait.portrait)
    articles = ArticleModel.query.filter_by(author_id=g.user.id)[0:2]
    # answer = AnswerModel.query.filter_by(author_id=g.user.id).first()
    functions = FunctionModel.query.filter_by(author_id=g.user.id)[0:2]

    if request.method == "GET":
        return render_template("user_space.html", users=my_portrait, f=f, articles=articles, functions=functions)


@bp.route("/Myspace/article", methods=["GET", "POST"])
def My_space_article():
    if request.method == "GET":
        articles = ArticleModel.query.filter_by(author_id=g.user.id).all()
        my_portrait = User_Model.query.filter_by(user=g.user.user).first()
        f = open(my_portrait.portrait)
        function = FunctionModel.query.filter_by(author_id=g.user.id)[0:2]
        articles = articles.items
        return render_template("user_space.html", users=my_portrait, f=f, articles=articles, function=function)


@bp.route("/Myspace/function", methods=["GET", "POST"])
def My_space_function():
    # if request.method == "GET":
    #     articles = ArticleModel.query.filter_by(author_id=g.user.id)[0:2]
    #     my_portrait = User_Model.query.filter_by(user=g.user.user).first()
    #     f = open(my_portrait.portrait)
    #     # function = db.session.query(FunctionModel).filter(FunctionModel.author_id == g.user.id).order_by(
    #     #     ArticleModel.create_time.desc()).paginate(page=page_id, per_page=2,
    #     #                                               error_out=False)
    #     # function = function.items
    #     function = FunctionModel.query.filter_by(author_id=g.user.id).all()
    #     return render_template("user_space.html", users=my_portrait, f=f, articles=articles, function=function)
    function_dict = []
    if request.method == "GET":
        functions = FunctionModel.query.filter_by(author_id=g.user.id).all()
        for function in functions:
            article_dict = {
                "article_id": function.article_id,
                "title": function.title,
                "content": function.content,
                "browse_number": function.browse_number,
                "likes_number": function.likes_number,
                "collection_number": function.collection_number,
                "photo": function.Photo,
                "create_time": function.create_time
            }
            function_dict.append(article_dict)
        return Response(json.dumps({"code": 200, "msg": "操作成功", "data": function_dict}, default=str),
                        mimetype='application/json')
    elif request.method == "POST":
        return global_setting.good_message()


@bp.route("/fenye")
def fenye():
    articles = ArticleModel.query.filter_by(author_id=g.user.id)[1]
    return render_template("fenye.html", articles=articles)
