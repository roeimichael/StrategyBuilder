import schedule
import time
import smtplib

from email.message import EmailMessage


def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "Moneymakerss007@gmail.com"
    password = "1Q2w3e4R"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)

    server.quit()


if __name__ == '__main__':
    schedule.every(1).days.do(email_alert)

    while True:
        schedule.run_pending()
        time.sleep(1)
