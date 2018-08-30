# Lesson2Cal: SJTU ElectSys课程表日历生成器

解析教学信息服务网页面，生成`.ics`文件（可导入Outlook、Google Calendar等多种日历服务）

开发中，目前使用网页作为前端；欢迎贡献其他前端！

## Install Dependencies

```
pip install -r requirements.txt
```

## Usage

```
./server.py
```

然后浏览器访问，默认地址为`http://127.0.0.1:5000/`。
输入账号、验证码、本学期第一周的周一日期并提交后，如果顺利，页面将生成一`output.ics`文件。
该文件为文本文件，在导入之前，如有需求可进行编辑。
一个事件的形式如下：
```
BEGIN:VEVENT
SUMMARY:课程名@地点
DTSTART:20180910T080000
DTEND:20180910T094000
RRULE:FREQ=WEEKLY;INTERVAL=1;COUNT=16
END:VEVENT
```
`SUMMARY`为事件的标题，`DTSTART`、`DTEND`分别为首次事件开始、结束的日期与时间；
`RRULE`控制事件的重复，可借助[RRULE Tool](https://icalendar.org/rrule-tool.html)生成。

## Known Issues

- 本程序不会储存或上传你的jAccount密码，使用时可善用浏览器的记住密码功能；
- 密码在前端后端之间明文传输，且线程不安全（共享`manager`），故不建议部署在公网上使用；
- 为了您的账户安全，不建议使用他人的部署；
- 目前的时间表示均没有附加时区信息；

## Disclaimer

存在解析错误的可能性，具体课表请以ElectSys为准。任何错误引起的不良后果，开发者恕不承担。

## To-Do

- use bootstrap
- threading safety
- time zone for ics
