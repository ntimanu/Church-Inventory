from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        STAFF = 'STAFF', _('Staff')
        VOLUNTEER = 'VOLUNTEER', _('Volunteer')
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.VOLUNTEER,
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    ministry_area = models.ForeignKey(
        'ministry_areas.MinistryArea',
        on_delete=models.SET_NULL,
        related_name='members',
        null=True,
        blank=True
    )
    bio = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Overriding USERNAME_FIELD to use email for authentication
    USERNAME_FIELD = 'email'
    # email is already in REQUIRED_FIELDS by default due to USERNAME_FIELD
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
        
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
        
    def is_staff_member(self):
        return self.role == self.Role.STAFF
        
    def is_volunteer(self):
        return self.role == self.Role.VOLUNTEER
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        