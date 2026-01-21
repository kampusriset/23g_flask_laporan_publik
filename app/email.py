import smtplib
from email.message import EmailMessage
from flask import current_app

def send_email(subject, recipients, text_body, html_body=None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    msg["To"] = ", ".join(recipients)
    
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype='html')

    try:
        smtp_server = current_app.config["MAIL_SERVER"]
        smtp_port = current_app.config["MAIL_PORT"]
        smtp_user = current_app.config["MAIL_USERNAME"]
        smtp_pass = current_app.config["MAIL_PASSWORD"]

        # Logika Pilihan Jalur (SSL vs TLS)
        if current_app.config.get("MAIL_USE_SSL"):
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            # Ini jalur buat BREVO (Port 587 / 2525)
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                if current_app.config.get("MAIL_USE_TLS"):
                    server.starttls()
                    server.ehlo()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                
        print(f"✅ Email sent to {recipients}")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise e # Lempar error biar ketangkep di route