import smtplib
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

time = datetime.now().timetuple()
today = str(time.tm_year) + '-' + str(time.tm_mon) + '-' + str(time.tm_mday)
msg_from = 'fengbx@xxx.com'  # 发送人邮箱
passwd = 'xxxxx'  # 密码，自己填
msg_to = 'fengbx@uxsino.com,tian_XXX@uXXX.com'  # 收件人邮箱，多人用英文逗号隔开

 # 创建一个带附件的实例
message = MIMEMultipart()
message['From'] = Header('冯冰雪', 'utf-8')   # 发起人名字，不填展示为空
message['To'] = Header('项目组成员', 'utf-8')  # 接收人名字，不填展示为空
subject = '3D机房-测试日报'+ today# 主体内容
message['Subject'] = Header(subject, 'utf-8')
file_html="daily_report.html"
with open('daily_report.html','r',encoding='utf-8') as f:
    content = f.read()
content = str(content)
print(content)
mail_msg = content
message.attach(MIMEText(mail_msg, 'html', 'utf-8')) # 如果要发送html需要将plain改成html

fp1 = open('ticket_summary_chart.png', 'rb')
msgImage1 = MIMEImage(fp1.read())
fp1.close()
msgImage1.add_header('Content-ID', '<image1>')
message.attach(msgImage1)

fp2 = open('daily_summary_chart.png', 'rb')
msgImage2 = MIMEImage(fp2.read())
fp2.close()
msgImage2.add_header('Content-ID', '<image2>')
message.attach(msgImage2)

fp3 = open('ticet_people_chart.png', 'rb')
msgImage3 = MIMEImage(fp3.read())
fp3.close()
msgImage3.add_header('Content-ID', '<image3>')
message.attach(msgImage3)

fp4 = open('ticet_resolve_chart.png', 'rb')
msgImage4 = MIMEImage(fp4.read())
fp4.close()
msgImage4.add_header('Content-ID', '<image4>')
message.attach(msgImage4)

fp5 = open('ticet_module_chart.png', 'rb')
msgImage5 = MIMEImage(fp5.read())
fp5.close()
msgImage5.add_header('Content-ID', '<image5>')
message.attach(msgImage5)


try:
    smtpObj = smtplib.SMTP_SSL("smtp.exmail.qq.com", 465)  # qq邮箱的smtp地址及端口号
    smtpObj.login(msg_from, passwd)
    smtpObj.sendmail(msg_from, msg_to, message.as_string())
    print ("成功")
except smtplib.SMTPException:
    print("失败")
