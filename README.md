# Lesson2Cal: SJTU ElectSys课程表日历生成器

解析教学信息服务网页面，生成`.ics`文件（可导入Outlook、Google Calendar等多种日历服务）

目前使用网页作为前端（Vue.js & Element UI）；欢迎贡献其他前端！

使用中遇到问题，或有意见或建议，可在Issue中提出。

## Install

对于Windows用户，可以直接在[Release页面](https://github.com/Tantalus13A98B5F/lesson2cal/releases)
下载内嵌Python和所有依赖的压缩包，解压后双击`start.bat`即可启动。注意，Release版本可能不会包括最新的功能。

如手动安装，请确保已安装Python 3.4或以上版本，且`pip`可用。下载本项目文件后执行：
```
pip install -r requirements.txt
```

## Usage

运行`./server.py`，浏览器将自动打开页面，默认地址为`http://localhost:5000/`。
输入相关信息后，如果顺利，页面将生成一`output.ics`文件。
该文件为文本文件，在导入之前，如有需要可进行编辑。
一个事件的形式如下：
```
BEGIN:VEVENT
SUMMARY:事件名称
DTSTART:20180910T080000
DTEND:20180910T094000
RRULE:FREQ=WEEKLY;INTERVAL=1;COUNT=16
END:VEVENT
```
`SUMMARY`为事件的标题，`DTSTART`、`DTEND`分别为首次事件开始、结束的日期与时间；
另有`LOCATION`、`DESCRIPTION`字段可选添加；
`RRULE`控制事件的重复，可借助[RRULE Tool](https://icalendar.org/rrule-tool.html)生成。

## Options

目前提供两个可配置项。

关于地点显示：
- `课程名称@地点`（默认）：地点显示在标题中，与超级课程表风格类似，对Outlook的Android Widget友好；
- `地点独立显示`：地点出现在专用的`LOCATION`字段中，但是Outlook的Android Widget不显示；

关于备注的处理：
- `不处理备注`：不读取备注信息，形策课将会每周出现；
- `仅处理形策`：形策课将被处理为数个不重复的事件；
- `仅处理教室未定的课程`：将处理课程表中显示为教室未定的课程，包括体育以及大部分的实验课、实践课；
- `仅处理形策和教室未定的课程`（默认）：相当于以上两条的组合
- `读取所有备注`：读取所有备注，并对形策特殊处理；但是为了防止被ElectSys封xu禁ming，每次读取前都将暂停5秒钟，因此可能耗费相当长的时间；

## Known Issues

- 本程序不会储存或上传你的jAccount密码，使用时可善用浏览器的记住密码功能；
- 密码在前端后端之间明文传输，且线程不安全（共享`manager`）、未作CSRF防御，故仅供本地使用，不宜用作公网服务；
- 为了您的账户安全，请谨慎使用他人的部署；

## Disclaimer

存在解析错误的可能性，具体课表请以ElectSys为准。任何错误引起的不良后果，开发者恕不承担。
