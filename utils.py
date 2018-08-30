from abc import ABCMeta, abstractmethod
from functools import wraps
from random import random
from urllib import parse
import logging
import requests


logger = logging.getLogger('lesson2cal')


def get_random():
    return random() * 10**8


def with_max_retries(count):
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(count):
                try:
                    ret = func(*args, **kwargs)
                except Exception as e:
                    logger.info('try %s: %r failed with %r', i, func, e)
                    if i == count - 1:
                        raise e
                else:
                    return ret
        return wrapper
    return real_decorator


class JAccountLoginManager(metaclass=ABCMeta):
    def __init__(self, session=None):
        self.session = session or requests.Session()
    
    def new_session(self):
        self.session = requests.Session()

    @abstractmethod
    def get_login_url(self) -> str:
        pass

    @abstractmethod
    def check_login_result(self, rsp) -> 'error':
        splitted = parse.urlsplit(rsp.request.url)
        if splitted.netloc == 'jaccount.sjtu.edu.cn':
            query = parse.parse_qs(splitted.query)
            err = query.get('err', [None])[0]
            if err == '0':
                return '用户名或密码不正确'
            elif err == '1':
                return '验证码不正确'
            elif err == '2':
                return '服务器故障，请稍后再试'
            else:
                return '未知登录错误'
        return ''

    @with_max_retries(3)
    def store_variables(self) -> {'returl', 'se', 'sid'}:
        rsp = self.session.get(self.get_login_url())
        logger.info('login page return at: %s', rsp.request.url)
        query = parse.urlsplit(rsp.request.url).query
        qs = parse.parse_qs(query)
        self.variables = {k: qs[k][0] for k in ('returl', 'se', 'sid')}

    @with_max_retries(3)
    def get_captcha(self) -> ('contenttype', 'body'):
        captcha_url = 'https://jaccount.sjtu.edu.cn/jaccount/captcha?%s'
        rsp = self.session.get(captcha_url % get_random())
        return rsp.headers['Content-Type'], rsp.content

    @with_max_retries(3)
    def post_credentials(self, user, passwd, captcha) -> bool:
        action_url = 'https://jaccount.sjtu.edu.cn/jaccount/ulogin'
        payload = {'user': user, 'pass': passwd, 'captcha': captcha}
        payload.update(self.variables)
        rsp = self.session.post(action_url, payload)
        logger.info('post return at: %s', rsp.request.url)
        return self.check_login_result(rsp)
