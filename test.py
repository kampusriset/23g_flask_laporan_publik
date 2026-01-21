import os
from app import create_app, mail
from flask_mail import Message
import smtplib

# 1. Bangunkan App-nya dulu
# (Otomatis baca .env karena logic create_app lu udah canggih)
app = create_app()

# 2. Masuk ke dalam "Ruang Mesin" (Context)
with app.app_context():
    print("-------------------------------------------------")
    print(f"🚀 Mencoba connect ke: {app.config['MAIL_SERVER']} port {app.config['MAIL_PORT']}")
    print(f"📧 Sender: {app.config['MAIL_DEFAULT_SENDER']}")
    print("-------------------------------------------------")

    try:
        # Bikin Pesan
        msg = Message(
            subject="Test Brevo dari Script",
            recipients=["rizkianasm@gmail.com"], # Ganti ke email lu sendiri
            body="Halo! Kalau email ini masuk, berarti settingan Brevo lu udah PERFECT! 🔥"
        )
        
        # Kirim!
        mail.send(msg)
        print("\n✅ SUKSES BESAR! Cek inbox (atau spam) email lu sekarang.")
    
    except smtplib.SMTPAuthenticationError:
        print("\n❌ ERROR: LOGIN GAGAL")
        print("Kemungkinan Password di .env lu salah.")
        print("Ingat: Pake SMTP Key dari dashboard Brevo, BUKAN password login web!")
        
    except smtplib.SMTPRecipientsRefused:
        print("\n❌ ERROR: DITOLAK BREVO")
        print("Kemungkinan 'MAIL_DEFAULT_SENDER' di .env lu belum diverifikasi di Brevo.")
        
    except Exception as e:
        print(f"\n❌ ERROR LAIN: {e}")