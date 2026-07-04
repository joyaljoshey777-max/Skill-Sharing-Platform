from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class User(AbstractUser):
    is_provider = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)

class ProviderProfile(models.fields.Field):
    pass # Replaced below

class ProviderProfile(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    experience = models.TextField()
    price_per_service = models.DecimalField(max_digits=10, decimal_places=2)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    id_proof = models.FileField(upload_to='id_proofs/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejecting the provider profile")
    contact_details = models.CharField(max_length=255, help_text="Email or Phone shown only on confirmed booking")

    def __str__(self):
        return f"{self.user.username}'s Profile - {self.status}"

class Skill(models.Model):
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    #description = model.models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='bookings_received')
    skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejecting the booking")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'date', 'time'],
                condition=models.Q(status='Confirmed'),
                name='unique_confirmed_booking_slot'
            )
        ]

    def __str__(self):
        return f"Booking for {self.provider.user.username} on {self.date} at {self.time}"

    def clean(self):
        if self.status == 'Confirmed':
            existing = Booking.objects.filter(
                provider=self.provider,
                date=self.date,
                time=self.time,
                status='Confirmed'
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError("This provider is already booked at this time.")

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.provider.user.username} - {self.rating} Stars"
