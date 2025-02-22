from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password


# Create your models here.
class Contact(models.Model):
    contact_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, null=True)  # Add skills field
    availability = models.CharField(max_length=255, blank=True, null=True)  # Add availability field
    contact_id = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Add this line
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=255, blank=True, null=True)  # Simple text password  
    approval_status = models.CharField(max_length=50, 
                                       choices=[('Pending', 'Pending'), ('Approved', 'Approved'), 
                                                ('Rejected', 'Rejected')], default="Pending")

    def set_password(self, raw_password):
        """Hashes the password and stores it."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifies the password."""
        return check_password(raw_password, self.password)

    def __str__(self):
        """Return a string representation of the contact, including first name, last name, and email."""
        return f"{self.first_name} {self.last_name} ({self.email})"
