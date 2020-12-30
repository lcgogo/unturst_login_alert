#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import smtplib,socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.base import MIMEBase
from email import encoders
import re
import os

dirname, filename = os.path.split(os.path.abspath(__file__))
if filename.split(".")[-1] == "py":
    conffilename = filename[:-3] + ".conf"
elif filename.split(".")[-1] == "pyc":
    conffilename = filename[:-4] + ".conf"
#print(conffilename)
conffile = dirname + "/" + conffilename

confDict = {}
with open(conffile, "r") as f:
    for line in f.readlines():
        if re.match(r'^#|^\s+#|^\s+', line) == None:   # remove the line which has # at the head
            key = line.split("=")[0].strip()
            value = line.split("=")[1].strip()
            if re.search("^\"|\'", value) and re.search("\"|\'$", value):
                value = value[1:-1]
            confDict[key] = value
from_addr = confDict["from_addr"]
smtp_user = confDict["smtp_user"]
smtp_server = confDict["smtp_server"]
smtp_port = confDict["smtp_port"]
password = confDict["password"]
devops_addr = confDict["devops_addr"]
debug_addr = confDict["debug_addr"]
#print(confDict)

# mailconffile is a file contains mail config like below:

# from_addr = 'name@example.com'
# smtp_server = 'smtp.exmail.qq.com'
# smtp_port = 465 # QQ企业邮箱端口465，用SMTP_SSL
# password = 'xxxxxxxxxxxx'
# devops_addr = "opsxxxxx@example.com"
# debug_addr = "name@example.com,namexxxx@example.com"


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
    Header(name, 'utf-8').encode(), \
    addr.encode('utf-8') if isinstance(addr, bytes) else addr))

## 输入Email地址和口令:
#from_addr = raw_input('From: ')
#password = raw_input('Password: ')
## 输入SMTP服务器地址:
#smtp_server = raw_input('SMTP server: ')
## 输入收件人地址:
#to_addr = raw_input('To: ')

def send_mail(title, message, debug, toaddr = None, *attachfile):
    hostname = socket.gethostname()
    msg = MIMEMultipart()
    #msg['From'] = _format_addr(u'Alert from %s <%s>' % (hostname,from_addr))
    msg['From'] = from_addr
    #msg['To'] = _format_addr(u'管理员<%s>' % to_addr)
    if debug == 0 and toaddr != None:
        to_addr = toaddr
    elif debug == 0 and toaddr == None:
        to_addr = devops_addr
    else:
        to_addr = debug_addr
    if debug != 0:
        title = "[DEBUG] " + title
    msg['To'] = _format_addr(to_addr)
    msg['Subject'] = Header(title, 'utf-8').encode()
    msg.attach(MIMEText('<html><body>' +
          '<p>' + message + '</p>' +
          '</body></html>', 'html', 'utf-8'))
    for emailfile in attachfile:
        with open(emailfile, 'r') as f:
            # 设置附件的MIME和文件名，这里是jpg类型:
            emailfilename = emailfile.split("/")[-1]
            filetype = emailfilename.split(".")[-1]
            #print(filename)
            #print(filetype)
            mime = MIMEBase('file', filetype, filename = emailfilename)
            # 加上必要的头信息:
            mime.add_header('Content-Disposition', 'attachment', filename = emailfilename)
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来:
            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            msg.attach(mime)
    server = smtplib.SMTP_SSL(smtp_server, smtp_port) # SMTP协议默认端口是25
    #server.starttls()
    server.set_debuglevel(1)
    server.login(smtp_user, password)
    server.sendmail(from_addr, to_addr.split(','), msg.as_string())
    server.quit()

def main():
    title = "test title"
    message = "test email. <br> 2nd line."
    attachfile = "/tmp/test.txt"
    debug = 1
    send_mail(title, message, debug, attachfile)
    #send_mail(title, message, debug)

if __name__ == '__main__':
    main()
