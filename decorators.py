from flask import g, redirect, url_for
from functools import wraps

from flask_mail import Message

import global_setting
from exts import mail, db
from models import Email_Captcha_Model


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if hasattr(g, "user"):
            return func(*args, **kwargs)
        else:
            return redirect(url_for("user.login"))

    return wrapper


class Email_Captcha:

    def email_code(self, email, captcha):  # 保存验证码
        email_moder = Email_Captcha_Model.query.filter_by(email=email).first()
        if email_moder:
            message = Message(subject="【安安的小屋】",
                              recipients=[email],
                              body=f"【安安的小屋】忘记密码了吗？,您的邮箱验证码是：{captcha},请勿告诉任何人哦")
            mail.send(message)
            db.session.query(Email_Captcha_Model).filter_by(email=email).update({"captcha": captcha})
            db.session.commit()
            return global_setting.good_message()
        else:
            email_id = "E" + global_setting.inset_token().upper()
            message = Message(subject="【安安的小屋】",
                              recipients=[email],
                              body=f"【安安的小屋】忘记密码了吗？,您的邮箱验证码是：{captcha},请勿告诉任何人哦")
            mail.send(message)
            captcha_moder = Email_Captcha_Model(email=email, captcha=captcha, email_id=email_id)
            db.session.add(captcha_moder)
            db.session.commit()

