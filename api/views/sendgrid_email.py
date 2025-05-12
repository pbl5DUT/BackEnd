# api/views/sendgrid_email.py
from django.http import JsonResponse
from rest_framework.decorators import api_view
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

@api_view(['POST'])
def send_password_email(request):
    email = request.data.get('email')  # Lấy email từ POST request
    password = request.data.get('password')  # Lấy password từ POST request

    if not email or not password:
        return JsonResponse({"status": "error", "detail": "Email and password are required"}, status=400)

    subject = "Your New Password"
    message = f"Here is your new password: {password}"

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        mail = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=email,
            subject=subject,
            plain_text_content=message
        )
        response = sg.send(mail)
        return JsonResponse({"status": "success", "detail": f"Email sent to {email}, status code: {response.status_code}"})
    except Exception as e:
        return JsonResponse({"status": "error", "detail": str(e)}, status=500)
