from .models import Notification


def notification_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by(
            "-created_at"
        )[0:3]
        unread = Notification.objects.filter(is_read=False)

        return {
            "notifications": notifications,
            "unread": unread,
        }
    return {}
