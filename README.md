# Lesson2Cal: SJTU ElectSys课程表日历生成器

解析教学信息服务网页面，生成`.ics`文件（可导入Outlook、Google Calendar等多种日历服务）

开发中，目前使用网页作为前端；欢迎贡献其他前端！

## Dependencies

- flask
- vobject
- requests
- bs4

## Usage

```
./server.py
```

然后浏览器访问，默认地址为`http://127.0.0.1:5000/`。

## Security Issues

- 本程序不会储存或上传你的jAccount密码，使用时可善用浏览器的记住密码功能；
- 密码在前端后端之间明文传输，故不建议部署在公网上使用；
- 不建议使用他人的部署；

## To-Do

- logging
- safe reloading
- threading safety
- time zone for ics
- add requirements.txt
