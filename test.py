import requests
from bs4 import BeautifulSoup

session = requests.session()

session.cookies.setdefault('JSESSIONID', 'EB78DA53D2BC35880B74CB49377343C7')
session.cookies.setdefault('SRV', 'f1e538f4-ff67-4d5c-bf16-69875eb1d47b')
session.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'


#
# url = 'http://i.sjtu.edu.cn/xtgl/index_initMenu.html'
# rsp = session.get(url)
# print(rsp.url)

# soup = BeautifulSoup(rsp.content, 'lxml')
# requestMap = soup.find(id='requestMap')
# su = requestMap.find(id='sessionUserKey').get('value')

#
url = 'http://i.sjtu.edu.cn/kbcx/xskbcx_cxXskbcxIndex.html'
rsp = session.get(url % su, params={
    'gnmkdm': 'N2151',
    'layout': 'default',
    'su': su
})
print(rsp.url)

xnm = soup.find(id='xnm2')
xqm = soup.find(id='xqm2')

#
url = 'http://i.sjtu.edu.cn/kbcx/xskbcx_cxXsKb.html'
rsp = session.post(url, data={
    'xnm': '2018',
    'xqm': '3'
}, params={
    'gnmkdm': 'N2151'
})
print(rsp.url)
