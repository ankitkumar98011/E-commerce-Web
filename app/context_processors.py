from .models import Notification

def notifications_context(request):
    """Context processor to add notifications data to all templates"""
    context = {
        'unread_notifications_count': 0,
    }
    
    if request.user.is_authenticated:
        context['unread_notifications_count'] = request.user.notifications.filter(is_read=False).count()
    
    return context
