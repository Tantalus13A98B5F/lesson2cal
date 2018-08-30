#!/usr/bin/env python3
import datetime as dt
import flask
from manager import ElectSysManager


app = flask.Flask(__name__)
manager = ElectSysManager()


@app.route('/')
def index_view():
    manager.store_variables()
    return flask.render_template('index.html')


@app.route('/captcha')
def captcha_view():
    contenttype, captcha = manager.get_captcha()
    response = flask.make_response(captcha)
    response.headers['Content-Type'] = contenttype
    return response


@app.route('/post', methods=['POST'])
def post_view():
    try:
        user = flask.request.form['user']
        passwd = flask.request.form['passwd']
        captcha = flask.request.form['captcha']
        firstday_raw = flask.request.form['firstday']
        firstday = dt.date(*[int(i) for i in firstday_raw.split('/')])
    except (KeyError, ValueError, TypeError):
        return '参数错误'
    if manager.post_credentials(user, passwd, captcha):
        cal = manager.convert_lessons_to_ics(firstday)
        response = flask.make_response(cal.serialize())
        response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename="output.ics"'
        return response
    else:
        return '登录失败'


if __name__ == '__main__':
    app.run(debug=True)
