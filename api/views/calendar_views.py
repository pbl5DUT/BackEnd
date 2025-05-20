from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.models.calendar import Calendar
from api.serializers import CalendarSerializer
from django.utils import timezone
from datetime import timedelta

@api_view(['GET', 'POST'])
def events(request):
    if request.method == 'GET':
        events = Calendar.objects.all()
        serializer = CalendarSerializer(events, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CalendarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_events_by_project(request, project_id):
    events = Calendar.objects.filter(project_id=project_id)  # hoặc project__id nếu là ForeignKey
    serializer = CalendarSerializer(events, many=True)
    return Response(serializer.data)
@api_view(['GET'])
def get_user_events(request):
    user_id = request.user.user_id  # Giả sử có auth
    events = Calendar.objects.filter(user_id=user_id)
    serializer = CalendarSerializer(events, many=True)
    print("User object:", request.user)
    print("User type:", type(request.user))
    print("User: ", request.user)
    print("Is Authenticated: ", request.user.is_authenticated)
    return Response(serializer.data)

@api_view(['PUT'])
def update_event(request, event_id):
    try:
        event = Calendar.objects.get(event_id=event_id)
    except Calendar.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = CalendarSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_event(request, event_id):
    try:
        event = Calendar.objects.get(event_id=event_id)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Calendar.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_upcoming_events(request):
    days = int(request.GET.get('days', 7))
    now = timezone.now()
    end_date = now + timedelta(days=days)
    events = Calendar.objects.filter(start__range=[now, end_date])
    serializer = CalendarSerializer(events, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def sync_google_calendar(request):
    # Mô phỏng - thay bằng logic thực tế nếu có
    return Response({"success": True, "message": "Google Calendar synced successfully."})
