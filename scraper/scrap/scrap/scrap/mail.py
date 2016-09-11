

class emailScrap(object):

    @staticmethod
    def send_mail( message, title):
        print "Sending mail..........."
        import smtplib
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEText import MIMEText
        from email.MIMEBase import MIMEBase
        from email import Encoders
        User = 'donjoseenriqueruiz@gmail.com'
        Password = 'pass'
        recipient = 'quique@enreda.coop'
        msg = MIMEMultipart()
        msg['From'] = User
        msg['To'] = recipient
        msg['Subject'] = title
        #add text plain
        msg.attach(MIMEText(message))
        #add log file
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open("failed.log", "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="failed.log"')
        msg.attach(part)

        mailServer = smtplib.SMTP('smtp.gmail.com', 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(User, Password)
        mailServer.sendmail(User, recipient, msg.as_string())
        mailServer.close()
        print "Mail sent"