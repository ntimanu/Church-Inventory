# Church Inventory System Database Models

This document outlines the database schema design for the Church Inventory Management System. It explains the models, their relationships, and the reasoning behind the design decisions.

## Overview

The database schema is designed around these core entities:

1. **Users** - Church staff and volunteers who manage inventory
2. **Ministry Areas** - Different departments or ministries within the church
3. **Categories** - Classifications for inventory items
4. **Items** - Physical assets being tracked
5. **Inventory Transactions** - Record of all inventory movements
6. **Maintenance Records** - History of item maintenance
7. **Item Checkouts** - Tracking of borrowed items

## Model Relationships Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │◄────┤MinistryArea │◄────┤    Item     │
└─────┬───────┘     └──────┬──────┘     └──────┬──────┘
      │                    │                   │
      │                    │                   │
      │                    │           ┌───────┴───────┐
      │                    │           │               │
┌─────▼───────┐     ┌──────▼──────┐   │┌─────────────┐│
│InventoryTran│     │    Item     │◄──┼┤  Category   ││
│  saction    │     │  Checkout   │   │└─────────────┘│
└─────────────┘     └─────────────┘   │               │
                                      │┌─────────────┐│
                                      └┤ Maintenance ││
                                       └─────────────┘
```

## User Model

```python
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        STAFF = 'STAFF', _('Staff')
        VOLUNTEER = 'VOLUNTEER', _('Volunteer')

    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(choices=Role.choices, default=Role.VOLUNTEER)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    ministry_area = models.ForeignKey('ministry_areas.MinistryArea', on_delete=models.SET_NULL, null=True)
    # Other fields from AbstractUser (username, first_name, last_name, etc.)
```

### Design Decisions:

- **Extending AbstractUser**: We've extended Django's AbstractUser model rather than using a separate profile model. This approach is cleaner for our needs since we're customizing the authentication process.
- **Role-based Access**: The Role choices field enables role-based permissions without requiring complex Django permission groups.
- **Email as Username**: By setting `USERNAME_FIELD = 'email'`, we're using email addresses for authentication which is more intuitive for users.
- **Ministry Area Relationship**: Users are associated with ministry areas to track which department they work with.

## Ministry Area Model

```python
class MinistryArea(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    leader = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='led_ministries')
    active = models.BooleanField(default=True)
    # Timestamps and other fields
```

### Design Decisions:

- **Slug Field**: Used for URL-friendly identifiers and better SEO.
- **Leader Relationship**: Each ministry has an optional leader via a ForeignKey to User.
- **Active Flag**: Allows ministries to be deactivated without deletion, preserving historical data.

## Category Model

```python
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
```

### Design Decisions:

- **Self-Reference**: The parent field allows for hierarchical categories (e.g., "Electronics" > "Audio Equipment" > "Microphones").
- **Unique Names**: Categories have unique names to prevent confusion.

## Item Model

```python
class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    ministry_area = models.ForeignKey('ministry_areas.MinistryArea', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=0)
    min_quantity = models.PositiveIntegerField(default=0)
    unit_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    condition = models.CharField(max_length=10, choices=Condition.choices)
    # Many other fields for tracking item details
```

### Design Decisions:

- **SET_NULL Relationships**: If a category or ministry area is deleted, items remain in the database with NULL values rather than being cascaded.
- **Condition Choices**: Standardized condition options ensure consistent reporting.
- **Minimum Quantity**: Helps with automatic low stock alerts.
- **Created/Updated Tracking**: We track both creation and last update timestamps and users.

## Inventory Transaction Model

```python
class InventoryTransaction(models.Model):
    class TransactionType(models.TextChoices):
        ADDITION = 'ADD', _('Addition')
        REMOVAL = 'REMOVE', _('Removal')
        ADJUSTMENT = 'ADJUST', _('Adjustment')
        TRANSFER = 'TRANSFER', _('Transfer')

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    quantity = models.IntegerField()
    previous_quantity = models.PositiveIntegerField()
    new_quantity = models.PositiveIntegerField()
    # Fields for tracking who, when, and why
```

### Design Decisions:

- **Immutable Records**: Transactions are designed to be immutable once created - they represent a point-in-time record.
- **Previous and New Quantities**: By storing both values, we maintain a complete audit trail.
- **CASCADE on Delete**: If an item is deleted, its transactions are also deleted as they have no meaning without the item.
- **Ministry Transfer Support**: We include from_ministry and to_ministry fields to track transfers between departments.

## Maintenance Model

```python
class Maintenance(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performed_by = models.CharField(max_length=200, blank=True)
    # Other maintenance tracking fields
```

### Design Decisions:

- **Item Relationship**: Directly linked to items for easy maintenance history tracking.
- **Cost Tracking**: Important for budgeting and asset value calculations.
- **Next Maintenance Date**: Supports maintenance scheduling and reminders.

## Item Checkout Model

```python
class ItemCheckout(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='checkouts')
    checked_out_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    checkout_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    quantity = models.PositiveIntegerField(default=1)
    checked_in_date = models.DateTimeField(null=True, blank=True)
    # Other checkout fields
```

### Design Decisions:

- **CASCADE on Delete**: If a user or item is deleted, their checkout records are also deleted.
- **Due Date**: Required field to track when items should be returned.
- **Checked In Date**: Nullable field that indicates whether an item has been returned.
- **Properties**: Calculated fields determine if a checkout is active or overdue.

## Signal Handlers

The system uses Django signals to maintain data integrity:

- When a new Item is created, an initial InventoryTransaction is automatically created.
- When quantities change, transactions are created to track the changes.

## Indexes and Performance Considerations

- Foreign keys are indexed by default in Django.
- Additional indexes could be added for frequently queried fields like `barcode` on Item model.
- `ordering` Meta options help with predictable query results.

## Security Considerations

- Sensitive data like user passwords are handled by Django's authentication system.
- CSRF protection is enabled for all forms.
- Permission checks ensure users can only access data appropriate to their role.
