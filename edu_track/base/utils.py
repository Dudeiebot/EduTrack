from django.core.mail import EmailMessage


def sendEmail(to_email, content, subject):
    email = EmailMessage(
        subject=subject,
        body=content,
        from_email="yooo@edutrack.com",
        to=[to_email],
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)
