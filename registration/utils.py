from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_confirmation_email(user):
    try:    
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        verification_url = f"http://localhost:4200/verify-email/{uid}/{token}"

        subject = "Bitte bestätige deine E-Mail-Adresse"
    
        # Textinhalt für E-Mail (für Clients, die HTML nicht unterstützen)
        text_content = f"Hallo {user.username},\n\nBitte bestätige deine E-Mail mit diesem Link:\n{verification_url}"

        # HTML-Inhalt für E-Mail
        html_content = f"""
        <html>
            <body>
            <div style="text-align: center;">
                <img src="http://localhost:4200/assets/images/logo.png" alt="Videoflix Logo" style="width: 250px; margin-bottom: 20px;">
            </div>
                <p>Dear {user.username},<p>
                <p>Thank you for registering with <a href="http://localhost:4200/">Videoflix</a>. To complete your registration and verify your email address, please click the link below:</p><br>
                <p><a href="{verification_url}" style="background-color: #2E3EDF; color: white; padding: 10px 20px;
                text-decoration: none; border-radius: 20px; display: inline-block;">
                    Activate account
                </a></p>
                <br>
                <p>If you did not create an account with us, please disregard this email.<br>
                <br>
                Best regards,<br>
                <br>
                Your Videoflix Team. <br>
            </body>
        </html>
        """

        # Email-Objekt erstellen
        email = EmailMultiAlternatives(subject, text_content, 'noreply@yourdeveloper.com', [user.email])

        # HTML-Alternative anhängen
        email.attach_alternative(html_content, "text/html")

        # Sende die E-Mail
        email.send()

        print("Email sent successfully. to {user.email}")

    except Exception as e:
        print(f"Error sending email: {e}")    
