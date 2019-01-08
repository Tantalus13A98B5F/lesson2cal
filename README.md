# Lesson2Cal: SJTU ElectSys课程表日历生成器

解析教学信息服务网页面，生成`.ics`文件（可导入Outlook、Google Calendar等多种日历服务）

目前使用网页作为前端（Vue.js & Element UI）；欢迎贡献其他前端！

使用中遇到问题，或有意见或建议，可在Issue中提出。

## Install

对于Windows用户，可以直接在[Release页面](https://github.com/Tantalus13A98B5F/lesson2cal/releases)
下载程序包，解压后双击`lesson2cal.exe`即可启动。注意，Release版本可能不会包括最新的功能。

如手动安装，请确保已安装Python 3.4或以上版本，且`pip`可用。下载本项目文件后执行以下语句安装依赖：
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

目前提供<del>两个</del>一个可配置项。

关于地点显示：
- `课程名称@地点`（默认）：地点显示在标题中，与超级课程表风格类似，对Outlook的Android Widget友好；
- `地点独立显示`：地点出现在专用的`LOCATION`字段中，但是Outlook的Android Widget不显示；

<del>关于备注的处理：</del>已经废弃，用户界面接口尚未删除
- 教务处表示以后开学两周内任课老师可以改上课地点
- 教务处还说形策会做分周显示，但是现在还看不到到底会怎么做

## 发行

采用`cx_Freeze`进行打包。这个包不在`requirements.txt`中，如有需求请安装`cx-freeze`。
- 打包请执行`python3 setup.py build`，产物在`build/`中
- 目前不支持Python 3.7，如有更新强迫受害者请自行解决（x）
- 目前没有解决相对路径问题，所以请一定在`lesson.exe`所在目录中直接运行
- 该脚本可以进行macOS上的打包，还可以用`bdist_dmg`命令生成dmg文件，但是路径和程序的生命周期不可控所以不可用

## Known Issues

- 本程序不会储存或上传你的jAccount密码，使用时可善用浏览器的记住密码功能；
- 密码在前端后端之间明文传输，且线程不安全（共享`manager`）、未作CSRF防御，故仅供本地使用，不宜用作公网服务；
- 为了您的账户安全，请谨慎使用他人的部署；

## Disclaimer

存在解析错误的可能性，具体课表请以ElectSys为准。任何错误引起的不良后果，开发者恕不承担。
