import wtforms
from wtforms.validators import length, email, EqualTo
from models import Email_Captcha_Model, User_Model
from flask import flash


class RegisterForm(wtforms.Form):
    """注册表单验证"""
    user = wtforms.StringField(validators=[length(min=4, max=20)])
    name = wtforms.StringField(validators=[length(min=2, max=20)])
    email = wtforms.StringField(validators=[email()])
    password = wtforms.StringField(validators=[length(min=6, max=20)])
    psd_two = wtforms.StringField(validators=[EqualTo("password")])
    captcha = wtforms.StringField(validators=[length(min=4, max=6)])

    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        captcha_model = Email_Captcha_Model.query.filter_by(email=email).first()
        if not captcha_model or captcha_model.captcha.lower() != captcha.lower():
            flash("邮箱验证码错误")
            raise wtforms.ValidationError("邮箱验证码错误")

    def validate_email(self, field):
        email = field.data
        user_model = User_Model.query.filter_by(email=email).first()
        if user_model:
            flash("邮箱已重复")
            raise wtforms.ValidationError("邮箱错误")

    def validate_user(self, field):
        user = field.data
        user_modrl = User_Model.query.filter_by(user=user).first()
        if user_modrl:
            flash("用户名重复")
            raise wtforms.ValidationError("用户名重复")

    def validate_name(self, field):
        name = field.data
        user_modrl = User_Model.query.filter_by(name=name).first()
        if user_modrl:
            flash("昵称重复")
            raise wtforms.ValidationError("昵称重复")


class LoginForm(wtforms.Form):
    """登录表单验证"""
    user = wtforms.StringField(validators=[length(min=4, max=20)])
    password = wtforms.StringField(validators=[length(min=6, max=20)])


class ArticleForm(wtforms.Form):
    """发布表单文章验证"""
    title = wtforms.StringField(validators=[length(min=4, max=50)])
    head = wtforms.StringField(validators=[length(min=4, max=50)])
    content = wtforms.StringField(validators=[length(min=4, max=10000)])


class QAFunctionForm(wtforms.Form):
    """发布问答表单验证"""
    title = wtforms.StringField(validators=[length(min=4, max=50)])
    content = wtforms.StringField(validators=[length(min=4, max=10000)])


class AnswerForm(wtforms.Form):
    """发布评论表单验证"""
    answer = wtforms.StringField(validators=[length(min=1)])


class Forgot_PasswordForm(wtforms.Form):
    """忘记密码表单验证"""
    user = wtforms.StringField(validators=[length(min=4, max=20)])
    email = wtforms.StringField(validators=[email()])
    password = wtforms.StringField(validators=[length(min=6, max=20)])
    psd_two = wtforms.StringField(validators=[EqualTo("password")])
    captcha = wtforms.StringField(validators=[length(min=4, max=6)])

    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        captcha_model = Email_Captcha_Model.query.filter_by(email=email).first()
        if not captcha_model or captcha_model.captcha.lower() != captcha.lower():
            flash("邮箱验证码错误")
            raise wtforms.ValidationError("邮箱验证码错误")

    def validate_user(self, field):
        user = field.data
        email = self.email.data
        usermodel = User_Model.query.filter_by(user=user).first()
        if usermodel:
            if usermodel.email != email:
                flash("用户名和邮箱不匹配")
                raise wtforms.ValidationError("用户名和邮箱不匹配")
        else:
            flash("用户不存在")
            raise wtforms.ValidationError("用户不存在")

    def validate_password(self, field):
        password = field.data
        psd_two = self.psd_two.data

        if password != psd_two:
            flash("两次密码不一致")
            raise wtforms.ValidationError("两次密码不一致")
