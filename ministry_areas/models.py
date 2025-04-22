from django.db import models
from django.utils.translation import gettext_lazy as _

class MinistryArea(models.Model):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    location = models.CharField(_('location'), max_length=100, blank=True)
    leader = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_ministries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('ministry area')
        verbose_name_plural = _('ministry areas')
        ordering = ['name']