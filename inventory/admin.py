from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Item, InventoryTransaction, Maintenance, ItemCheckout

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model.
    """
    list_display = ('name', 'parent', 'description')
    search_fields = ('name', 'description')
    list_filter = ('parent',)


class MaintenanceInline(admin.TabularInline):
    """
    Inline admin for Maintenance records within Item admin.
    """
    model = Maintenance
    extra = 0


class InventoryTransactionInline(admin.TabularInline):
    """
    Inline admin for InventoryTransaction records within Item admin.
    """
    model = InventoryTransaction
    extra = 0
    readonly_fields = ('transaction_date', 'conducted_by')
    fields = ('transaction_type', 'quantity', 'previous_quantity', 'new_quantity', 
              'from_ministry', 'to_ministry', 'reason', 'transaction_date', 'conducted_by')
    max_num = 10  # Limit the number of transactions shown
    can_delete = False


class ItemCheckoutInline(admin.TabularInline):
    """
    Inline admin for ItemCheckout records within Item admin.
    """
    model = ItemCheckout
    extra = 0
    fields = ('checked_out_by', 'checkout_date', 'due_date', 'quantity', 
              'purpose', 'checked_in_date')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    Admin interface for Item model.
    """
    list_display = ('name', 'category', 'ministry_area', 'quantity', 'display_total_value', 
                   'condition', 'needs_reorder_flag')
    list_filter = ('category', 'ministry_area', 'condition', 'acquisition_date')
    search_fields = ('name', 'description', 'barcode', 'location')
    inlines = [MaintenanceInline, InventoryTransactionInline, ItemCheckoutInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category', 'ministry_area')
        }),
        ('Inventory Details', {
            'fields': ('quantity', 'min_quantity', 'unit_value', 'barcode')
        }),
        ('Item Information', {
            'fields': ('condition', 'acquisition_date', 'location', 'image', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_by', 'last_updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def display_total_value(self, obj):
        """Display the total value with currency formatting"""
        return f"${obj.total_value:.2f}"
    display_total_value.short_description = 'Total Value'
    
    def needs_reorder_flag(self, obj):
        """Display a visual indicator if item needs reordering"""
        if obj.needs_reorder:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Low Stock</span>')
        return format_html('<span style="color: green;">✓ In Stock</span>')
    needs_reorder_flag.short_description = 'Stock Status'
    
    def save_model(self, request, obj, form, change):
        """Override save_model to track user who created/updated the item"""
        if not change:  # If creating a new object
            obj.created_by = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Override save_formset to track user for transactions"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, InventoryTransaction) and not instance.pk:
                instance.conducted_by = request.user
            instance.save()
        formset.save_m2m()


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for InventoryTransaction model.
    """
    list_display = ('item', 'transaction_type', 'quantity', 'previous_quantity', 
                   'new_quantity', 'conducted_by', 'transaction_date')
    list_filter = ('transaction_type', 'transaction_date', 'from_ministry', 'to_ministry')
    search_fields = ('item__name', 'reason', 'conducted_by__username')
    date_hierarchy = 'transaction_date'
    readonly_fields = ('previous_quantity', 'new_quantity', 'transaction_date')


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    """
    Admin interface for Maintenance model.
    """
    list_display = ('item', 'maintenance_date', 'performed_by', 'cost', 'next_maintenance_date')
    list_filter = ('maintenance_date', 'next_maintenance_date', 'internal_staff')
    search_fields = ('item__name', 'description', 'performed_by')
    date_hierarchy = 'maintenance_date'


@admin.register(ItemCheckout)
class ItemCheckoutAdmin(admin.ModelAdmin):
    """
    Admin interface for ItemCheckout model.
    """
    list_display = ('item', 'checked_out_by', 'checkout_date', 'due_date', 
                   'quantity', 'checked_in_date', 'checkout_status')
    list_filter = ('checkout_date', 'due_date', 'checked_in_date')
    search_fields = ('item__name', 'checked_out_by__username', 'purpose')
    date_hierarchy = 'checkout_date'
    
    def checkout_status(self, obj):
        """Display checkout status with color indicators"""
        if obj.checked_in_date:
            return format_html('<span style="color: green;">Returned</span>')
        elif obj.is_overdue:
            return format_html('<span style="color: red; font-weight: bold;">Overdue</span>')
        else:
            return format_html('<span style="color: orange;">Checked Out</span>')
    checkout_status.short_description = 'Status'