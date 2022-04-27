import smtplib
from email import message
from decouple import config


def send_mail(email_address, code):
    from_address = config('MAIL_ADDRESS')
    mail_password = config('MAIL_PASSWORD')

    smtp_host = 'smtp.gmail.com'  # メールサーバ
    smtp_port = 587  # メールサーバのポート
    from_email = from_address  # 送信元
    to_email = email_address  # 送信先
    username = from_email
    password = mail_password

    title = 'Verify Code'
    description = f'Verify Code is 【 {code} 】'

    # 送信メールの作成
    msg = message.EmailMessage()
    msg.set_content(description)
    msg['Subject'] = title
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP(smtp_host, smtp_port) as smtpobj:
        smtpobj.starttls()
        smtpobj.login(username, password)
        smtpobj.send_message(msg)


if __name__ == '__main__':
    send_mail('yui.0g.0418@gmail.com', '045343')
    # pass
