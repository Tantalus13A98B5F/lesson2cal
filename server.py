#!/usr/bin/env python3
from urllib import parse
import datetime as dt
import logging
import flask
import threading
import webbrowser
import json
from manager import ElectSysManager
from utils import *


logger = logging.getLogger('lesson2cal')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

app = flask.Flask(__name__)
manager = ElectSysManager()
threading.Timer(2, lambda: webbrowser.open('http://localhost:5000/')).start()


@app.route('/')
def index_view():
    manager.new_session()
    manager.store_variables()
    return load_text_file(find_data_file('templates', 'index.html'))


@app.route('/captcha')
def captcha_view():
    contenttype, captcha = manager.get_captcha()
    response = flask.make_response(captcha)
    response.headers['Content-Type'] = contenttype
    return response


@app.route('/login', methods=['POST'])
def login_view():
    try:
        user = flask.request.form['user']
        passwd = flask.request.form['passwd']
        captcha = flask.request.form['captcha']
    except (KeyError, ValueError, TypeError):
        return flask.jsonify({'success': False, 'message': '参数错误'})
    error = manager.post_credentials(user, passwd, captcha)
    if not error:
        return flask.jsonify({'success': True, 'data': manager.get_raw_data()})
    else:
        return flask.jsonify({'success': False, 'message': error})


@app.route('/post', methods=['POST'])
def post_view():
    try:
        firstday_raw = flask.request.form['firstday']
        firstday = dt.date(*[int(i) for i in firstday_raw.split('/')])
        calendar_style = json.loads(flask.request.form['style'])
    except (KeyError, ValueError, TypeError):
        return flask.jsonify({'success': False, 'message': '参数错误'})
    cal = manager.convert_lessons_to_ics(firstday, calendar_style)
    response = flask.make_response(cal.serialize())
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename="output.ics"'
    return response


if __name__ == '__main__':
    app.run()
