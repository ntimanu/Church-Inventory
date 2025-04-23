from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    """
    Model representing categories for inventory items.
    
    Categories allow for better organization and filtering of inventory.
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']


class Item(models.Model):
    """
    Model representing individual inventory items.
    
    This is the core model for tracking inventory in the church.
    """
    class Condition(models.TextChoices):
        NEW = 'NEW', _('New')
        EXCELLENT = 'EXCELLENT', _('Excellent')
        GOOD = 'GOOD', _('Good')
        FAIR = 'FAIR', _('Fair')
        POOR = 'POOR', _('Poor')
        DAMAGED = 'DAMAGED', _('Damaged')
    
    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='items'
    )
    ministry_area = models.ForeignKey(
        'ministry_areas.MinistryArea',
        on_delete=models.SET_NULL,
        null=True,
        related_name='items'
    )
    quantity = models.PositiveIntegerField(_('quantity'), default=0)
    min_quantity = models.PositiveIntegerField(_('minimum quantity'), default=0, 
                                              help_text=_('Minimum quantity before reordering'))
    unit_value = models.DecimalField(
        _('unit value'), 
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    acquisition_date = models.DateField(_('acquisition date'), null=True, blank=True)
    condition = models.CharField(
        _('condition'), 
        max_length=10, 
        choices=Condition.choices,
        default=Condition.GOOD
    )
    location = models.CharField(_('storage location'), max_length=100, blank=True)
    barcode = models.CharField(_('barcode'), max_length=100, blank=True, null=True, unique=True)
    image = models.ImageField(_('image'), upload_to='inventory/', blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_items'
    )
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_items'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def total_value(self):
        """Calculate the total value of this item (quantity * unit_value)"""
        return self.quantity * self.unit_value
    
    @property
    def needs_reorder(self):
        """Check if the item needs to be reordered based on minimum quantity"""
        return self.quantity <= self.min_quantity
    
    class Meta:
        verbose_name = _('inventory item')
        verbose_name_plural = _('inventory items')
        ordering = ['name']


class InventoryTransaction(models.Model):
    """
    Model for tracking all changes to inventory items.
    
    This provides a complete audit trail of inventory movements.
    """
    class TransactionType(models.TextChoices):
        ADDITION = 'ADD', _('Addition')
        REMOVAL = 'REMOVE', _('Removal')
        ADJUSTMENT = 'ADJUST', _('Adjustment')
        TRANSFER = 'TRANSFER', _('Transfer')
    
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
    )
    quantity = models.IntegerField(_('quantity'))
    previous_quantity = models.PositiveIntegerField(_('previous quantity'))
    new_quantity = models.PositiveIntegerField(_('new quantity'))
    from_ministry = models.ForeignKey(
        'ministry_areas.MinistryArea',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_transactions'
    )
    to_ministry = models.ForeignKey(
        'ministry_areas.MinistryArea',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_transactions'
    )
    reason = models.TextField(_('reason'), blank=True)
    conducted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventory_transactions'
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.item.name} ({self.quantity})"
    
    class Meta:
        verbose_name = _('inventory transaction')
        verbose_name_plural = _('inventory transactions')
        ordering = ['-transaction_date']


@receiver(post_save, sender=Item)
def update_item_quantity(sender, instance, created, **kwargs):
    """
    Signal handler to create a transaction record when an item is first created.
    
    This ensures we have a transaction record for the initial inventory.
    """
    if created:
        InventoryTransaction.objects.create(
            item=instance,
            transaction_type=InventoryTransaction.TransactionType.ADDITION,
            quantity=instance.quantity,
            previous_quantity=0,
            new_quantity=instance.quantity,
            reason="Initial inventory creation",
            conducted_by=instance.created_by
        )


class Maintenance(models.Model):
    """
    Model for tracking maintenance activities on inventory items.
    
    This helps track the service history and condition of items.
    """
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='maintenance_records'
    )
    maintenance_date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performed_by = models.CharField(max_length=200, blank=True)
    internal_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maintenance_supervised'
    )
    next_maintenance_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Maintenance for {self.item.name} on {self.maintenance_date}"
    
    class Meta:
        ordering = ['-maintenance_date']


class ItemCheckout(models.Model):
    """
    Model for tracking when items are checked out temporarily.
    
    This allows tracking of items that are loaned out but expected to return.
    """
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='checkouts'
    )
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='item_checkouts'
    )
    checkout_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    quantity = models.PositiveIntegerField(default=1)
    purpose = models.TextField(blank=True)
    checked_in_date = models.DateTimeField(null=True, blank=True)
    
    @property
    def is_overdue(self):
        """Check if the item checkout is overdue"""
        from django.utils import timezone
        if self.checked_in_date:
            return False
        return timezone.now().date() > self.due_date
    
    @property
    def is_active(self):
        """Check if the checkout is still active (not returned)"""
        return self.checked_in_date is None
    
    def __str__(self):
        return f"{self.item.name} - checked out by {self.checked_out_by.get_full_name()}"
    
    class Meta:
        ordering = ['-checkout_date']