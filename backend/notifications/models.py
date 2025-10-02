from accounts.models import User
from django.db import models


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("order_placed", "Order Placed"),
        ("order_confirmed", "Order Confirmed"),
        ("payment_received", "Payment Received"),
        ("order_shipped", "Order Shipped"),
        ("order_delivered", "Order Delivered"),
        ("product_review", "Product Review"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"
