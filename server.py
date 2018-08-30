#!/usr/bin/env python3
from urllib import parse
import datetime as dt
import logging
import flask
from manager import ElectSysManager


logger = logging.getLogger('lesson2cal')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
app = flask.Flask(__name__)
manager = ElectSysManager()


def redirect_error(msg):
    return flask.redirect('/?' + parse.urlencode({'error': msg}))


@app.route('/')
def index_view():
    error = flask.request.args.get('error')
    manager.new_session()
    return flask.render_template('index.html', error=error)


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
        return redirect_error('参数错误')
    manager.store_variables()
    error = manager.post_credentials(user, passwd, captcha)
    if not error:
        cal = manager.convert_lessons_to_ics(firstday)
        response = flask.make_response(cal.serialize())
        response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename="output.ics"'
        return response
    else:
        return redirect_error(error)


if __name__ == '__main__':
    app.run(debug=True)
