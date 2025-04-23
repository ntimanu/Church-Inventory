from django.contrib import admin
from .models import MinistryArea

@admin.register(MinistryArea)
class MinistryAreaAdmin(admin.ModelAdmin):
    """
    Admin interface for MinistryArea model.
    """
    list_display = ('name', 'location', 'leader', 'active')
    list_filter = ('active', 'location')
    search_fields = ('name', 'description', 'location')
    prepopulated_fields = {'slug': ('name',)}
    
    def get_queryset(self, request):
        """Get the queryset for the admin view, including related leader objects"""
        return super().get_queryset(request).select_related('leader')