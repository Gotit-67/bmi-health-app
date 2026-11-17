轻盈 BMI · Windows 数据库版

适用 Windows 10/11、Windows Server（含无图形桌面版本）。
需要 Python 3.10 或以上版本，安装 Python 时勾选 Add Python to PATH。
这是可运行源码安装包，不是免安装 EXE。首次安装需联网下载依赖。

一、本机运行
1. 解压 ZIP，整个文件夹保持在一起。
2. 双击 install.bat 安装依赖。
3. 双击 start.bat 启动，终端保持打开。
4. 浏览器打开 http://127.0.0.1:8501
5. 注册账号，再登录使用。

二、Windows Server 无桌面运行
把整个文件夹上传至 C:\bmi-windows-db。
在 PowerShell 执行：
  cd C:\bmi-windows-db
  .\install.bat
  .\start.bat
这些操作需要先在服务器上安装 Python，而不是只在自己电脑安装。
停止程序：Ctrl+C。重启服务器后需重新启动 start.bat。
本包不自动修改防火墙，不自动设开机启动。
公网访问还需公网 IP、阿里云安全组与 Windows 防火墙允许 TCP 8501。
公网部署如使用真实健康数据，应另配 HTTPS；本包本地默认 HTTP。

三、数据库
首次运行自动建立 data/bmi.sqlite3，无需另装数据库软件。
users：账号、密码派生哈希和随机盐（不存明文密码）。
measurements：测量时间、身高、体重、BMI 和结果。
foods：食物和记录时间。
exercise：每日运动时长和更新时间，同一天再次保存会覆盖当天时长。
每个账号只读取和删除自己的记录。饮食和运动面板显示北京时间当天记录。
BMI 历史保留全部测量，支持导出 CSV。
关闭程序、重新登录后记录恢复。备份时停止程序并复制 data 文件夹。
不要把 data 文件夹发给他人或上传到公开代码仓库。
此前旧版会话记录不在本包中，不会自动导入。

四、图片
尚未收到原图片。本包使用原配色，缺图不阻止运行。
将 health-pet.png 与 health-pyramid.png 放在 assets 文件夹，重启恢复。

五、修复
修复肥胖健康手册报错；历史测量显示保存的身高/体重，避免输入改变导致结果不一致。
自定义饮食文字做 HTML 转义。

六、验证范围
在 Linux 测试环境检查 Python 语法、数据库持久化、账号隔离、四类健康手册和页面交互。
Windows BAT 提供标准命令，但未在真实 Windows Server 执行。
本包尚未替你部署到阿里云。
