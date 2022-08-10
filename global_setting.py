import time
import hashlib
from flask import jsonify


def t_stamp():
    """转换时间格式"""
    t = time.time()
    t_tamp = int(t)
    return t_tamp


def inset_token():
    """生成token"""
    API_SECRET = 'JIANGAN'
    project_code = "test"
    account = "jiangan"
    time_stamp = str(t_stamp())
    h1 = hashlib.md5()
    strs = project_code + account + time_stamp + API_SECRET
    h1.update(strs.encode("utf-8"))
    user_token = h1.hexdigest()
    return user_token


def lack_request_parameters():
    return jsonify({"return_code": 415, "return_result": "请求参数错误"})


def not_request_parameters():
    return jsonify({"return_code": 400, "return_result": "请求参数为空"})


def server_error():
    return jsonify({"return_code": 500, "return_result": "服务器错误"})


def user_not_login():
    return jsonify({'return_code': '401', 'return_info': '用户未登录'})


def good_message():
    return jsonify({"code": 200, "msg": "操作成功"})
