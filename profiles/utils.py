from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def send_password_reset_email(user):
    try:    
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{uid}/{token}"

        subject = "Passwort zurücksetzen"
    
        text_content = f"Hallo {user.username},\n\nUm Ihr Passwort zurückzusetzen, klicken Sie bitte auf diesen Link:\n{reset_url}\n\nDer Link ist 24 Stunden gültig."

        html_content = f"""
        <html>
            <body>
            <div style="text-align: center;">
                <img src="{settings.FRONTEND_URL}/assets/images/logo.png" alt="Logo" style="width: 250px; margin-bottom: 20px;">
            </div>
                <p>Hallo {user.username},<p>
                <p>Sie haben angefordert, Ihr Passwort zurückzusetzen. Klicken Sie bitte auf den folgenden Button, um ein neues Passwort festzulegen:</p><br>
                <p><a href="{reset_url}" style="background-color: #2E3EDF; color: white; padding: 10px 20px;
                text-decoration: none; border-radius: 20px; display: inline-block;">
                    Passwort zurücksetzen
                </a></p>
                <br>
                <p>Der Link ist 24 Stunden gültig. Wenn Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail einfach.<br>
                <br>
                Mit freundlichen Grüßen,<br>
                <br>
                Ihr Team<br>
            </body>
        </html>
        """

        email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        print(f"Password reset email sent successfully to {user.email}")

    except Exception as e:
        print(f"Error sending password reset email: {e}")