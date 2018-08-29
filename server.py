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
    except KeyError:
        return '登录失败'
    if manager.post_credentials(user, passwd, captcha):
        from pprint import pprint
        pprint(manager.extract_lessons())
        return '登录成功'
    else:
        return '登录失败'


if __name__ == '__main__':
    app.run(debug=True)
