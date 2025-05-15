from django.http import JsonResponse
from django.views.decorators.http import require_GET
from api.models.user import User

@require_GET
def check_email_exists(request):
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'error': 'Email parameter is required.'}, status=400)

    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})