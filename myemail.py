import smtplib
from ecp import ecp_sign
from email.message import EmailMessage
import email
import imaplib
import base64
from os.path import basename
from email.mime.text import MIMEText
from email.header    import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE
import os 

class SMTPClient:
    def __init__(self, server, port, login, password):
        self.login = login
        self.server = smtplib.SMTP_SSL(server, port)
        self.server.ehlo()
        self.server.login(login, password)

    def send(self, to, subject, message, cert, attachment=None):
        if attachment:
            file = open(attachment, 'rb').read()
            file_sign = str(ecp_sign(file, cert))
        else:
            file_sign = "0x0"
        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.login
        msg['To'] = COMMASPACE.join(to)
        sign = f'\nFile signature: {file_sign} \nText signature: {ecp_sign(message.strip().encode(), cert)}'
        msg.attach(MIMEText(message+sign, 'plain', 'utf-8'))
        if attachment:
            part = MIMEApplication(file, Name=basename(attachment))
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment)
            msg.attach(part)

        self.server.sendmail(msg['From'], msg['To'], msg.as_string().encode('utf-8'))


class IMAPClient:
    def __init__(self, server, port, login, password):
        self.login = login
        self.server = imaplib.IMAP4_SSL(server, port)
        self.server.login(login, password)
        self.server.select('inbox') 

    def get(self):
        result, data = self.server.uid('search', None, "ALL") # Выполняет поиск и возвращает UID писем.
        latest_email_uid = data[0].split()[-1]
        result, data = self.server.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

        print(email_message)
        payload = self.get_body(email_message)

        try:
            print(email_message["Subject"])
            subject = base64.b64decode(email_message["Subject"].split('?')[-2]).decode()
        except Exception as er:
            print(er)
            try:
                subject = email_message["Subject"].split('?')[-2]
            except:
                subject = email_message["Subject"]
        
        filepath = self.get_attachment(email_message)

        return (email_message['From'], subject, payload, filepath)

    def get_body(self, email_message):
        msg = email_message
        if msg.is_multipart():
            html = None
            for part in msg.get_payload():
                print("%s, %s" % (part.get_content_type(), part.get_content_charset()))

                if part.get_content_charset() is None:
                    # We cannot know the character set, so return decoded "something"
                    text = part.get_payload(decode=True)
                    continue

                charset = part.get_content_charset()

                if part.get_content_type() == 'text/plain':
                    if part.get('Content-Transfer-Encoding') == "base64":
                        return base64.b64decode(part.get_payload()).decode().strip()
                    text = str(part.get_payload(decode=True), str(charset), "ignore").encode()

                if part.get_content_type() == 'text/html':
                    html = str(part.get_payload(decode=True), str(charset), "ignore").encode()

                if text is not None:
                    return text.strip()
                else:
                    return html.strip()
        else:
            text = str(msg.get_payload(decode=True), msg.get_content_charset(), 'ignore').encode()
            return text.strip()

    def get_attachment(self, email_message):
        msg = email_message
        att_path = None
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            att_path = os.path.join('./downloads', filename)

            if not os.path.isfile(att_path):
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
        return att_path