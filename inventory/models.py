from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Category(models.Model):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']

class Item(models.Model):
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
    min_quantity = models.PositiveIntegerField(_('minimum quantity'), default=0)
    unit_value = models.DecimalField(_('unit value'), max_digits=10, decimal_places=2, default=0)
    acquisition_date = models.DateField(_('acquisition date'), null=True, blank=True)
    condition = models.CharField(_('condition'), max_length=50, blank=True)
    location = models.CharField(_('storage location'), max_length=100, blank=True)
    barcode = models.CharField(_('barcode'), max_length=100, blank=True, unique=True)
    image = models.ImageField(_('image'), upload_to='inventory/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def total_value(self):
        return self.quantity * self.unit_value
    
    class Meta:
        verbose_name = _('inventory item')
        verbose_name_plural = _('inventory items')
        ordering = ['name']

class InventoryTransaction(models.Model):
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
        return f"{self.transaction_type} - {self.item.name} ({self.quantity})"
    
    class Meta:
        verbose_name = _('inventory transaction')
        verbose_name_plural = _('inventory transactions')
        ordering = ['-transaction_date']