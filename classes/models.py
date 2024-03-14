import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings

User = get_user_model()

class OnlineClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_classes')
    attendees = models.ManyToManyField(User, through='ClassEnrollment', related_name='enrolled_classes')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        title_has_changed = False

        if self.pk:
            orig = OnlineClass.objects.filter(pk=self.pk).first()
            if orig and orig.title != self.title:
                title_has_changed = True

        if not self.slug or title_has_changed:
            self.slug = slugify(self.title)
            unique_slug = self.slug
            num = 1
            while OnlineClass.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f'{self.slug}-{num}'
                num += 1
            self.slug = unique_slug

        super().save(*args, **kwargs)

class ClassEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    online_class = models.ForeignKey(OnlineClass, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    STATUS_CHOICES= (
        ('Active', 1),
        ('Cancelled', 0),
    )
    enrollment_status = models.CharField(choices=STATUS_CHOICES, blank=True, null=True, max_length=50, default='Active')


    def __str__(self):
        return f"{self.user.username} enrollment for {self.online_class.title}"


class ClassBackgroundImage(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='static/backgrounds/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class ClassMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_id = models.CharField(max_length=255)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='static/messages/files/', blank=True, null=True)  # For files and voice messages
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} in class {self.class_id}"    