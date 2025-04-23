# Church Inventory Management System - Database Schema

This document outlines the database schema for the Church Inventory Management System, including model relationships, field definitions, and design decisions.

## Overview

The database is structured around these core models:

1. **User** - Custom user model with role-based permissions
2. **MinistryArea** - Different departments/ministries in the church
3. **Category** - Classification for inventory items
4. **Item** - Core inventory item records
5. **InventoryTransaction** - Audit trail of all inventory changes
6. **Maintenance** - Records of item maintenance/service
7. **ItemCheckout** - Tracking of items temporarily checked out

## Entity Relationship Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│    User     │     │ MinistryArea │     │  Category   │
├─────────────┤     ├──────────────┤     ├─────────────┤
│ id          │┐   ┌│ id           │    ┌│ id          │
│ username    ││   ││ name         │    ││ name        │
│ email       ││   ││ slug         │    ││ description │
│ password    ││   ││ description  │    ││ parent      │┐
│ first_name  ││   ││ location     │    │└─────────────┘│
│ last_name   ││   ││ leader       │┐   └───────────────┘
│ role        ││   ││ active       ││
│ phone_number││   ││ notes        ││
│ ministry    │┘   ││ created_at   ││
│ bio         │    ││ updated_at   ││
│ date_joined │    │└──────────────┘│
│ last_updated│    └────────────────┘
└─────────────┘             │
       ┌──────────────┐     │
       │              │     │
       ▼              │     ▼
┌─────────────┐     ┌──────────────┐
│    Item     │     │ Maintenance  │
├─────────────┤     ├──────────────┤
│ id          │     │ id           │
│ name        │     │ item         │┐
│ description │     │ maint_date   ││
│ category    │┐    │ description  ││
│ ministry    │┘    │ cost         ││
│ quantity    │     │ performed_by ││
│ min_quantity│     │ internal_staff││
│ unit_value  │     │ next_date    ││
│ acq_date    │     │ created_at   ││
│ condition   │     └──────────────┘│
│ location    │     └───────────────┘
│ barcode     │            ▲
│ image       │            │
│ notes       │            │
│ created_by  │┐           │
│ updated_by  ││           │
│ created_at  ││           │
│ updated_at  ││           │
└─────────────┘│           │
└──────────────┘           │
       │                   │
       │                   │
       ▼                   │
┌────────────────┐         │
│InventoryTrans. │         │
├────────────────┤         │
│ id             │         │
│ item           │┐        │
│ trans_type     ││        │
│ quantity       ││        │
│ prev_quantity  ││        │
│ new_quantity   ││        │
│ from_ministry  ││        │
│ to_ministry    ││        │
│ reason         ││        │
│ conducted_by   ││        │
│ trans_date     ││        │
└────────────────┘│        │
└─────────────────┘        │
       │                   │
       │                   │
       ▼                   │
┌────────────────┐         │
│  ItemCheckout  │         │
├────────────────┤         │
│ id             │         │
│ item           │┐        │
│ checked_out_by ││        │
│ checkout_date  ││        │
│ due_date       ││        │
│ quantity       ││        │
│ purpose        ││        │
│ checked_in_date││        │
└────────────────┘│        │
└─────────────────┘        │
                           │
                           │
```

## Model Relationships

### User Model

The User model extends Django's AbstractUser to provide role-based access control:

- **OneToMany**: A User can be the leader of multiple MinistryAreas (`led_ministries`)
- **ManyToOne**: A User belongs to one MinistryArea (`ministry_area`)
- **OneToMany**: A User can create multiple Items (`created_items`)
- **OneToMany**: A User can update multiple Items (`updated_items`)
- **OneToMany**: A User can conduct multiple InventoryTransactions (`inventory_transactions`)
- **OneToMany**: A User can supervise multiple Maintenance records (`maintenance_supervised`)
- **OneToMany**: A User can check out multiple Items (`item_checkouts`)

### MinistryArea Model

Represents different church departments or ministries:

- **ManyToOne**: A MinistryArea can have one User as leader (`leader`)
- **OneToMany**: A MinistryArea can have multiple Users as members (`members`)
- **OneToMany**: A MinistryArea can have multiple Items (`items`)
- **OneToMany**: A MinistryArea can have outgoing InventoryTransactions (`outgoing_transactions`)
- **OneToMany**: A MinistryArea can have incoming InventoryTransactions (`incoming_transactions`)

### Category Model

Hierarchical classification system for inventory items:

- **ManyToOne**: A Category can have a parent Category (`parent`)
- **OneToMany**: A Category can have multiple child Categories (`children`)
- **OneToMany**: A Category can have multiple Items (`items`)

### Item Model

Core model for inventory items:

- **ManyToOne**: An Item belongs to one Category (`category`)
- **ManyToOne**: An Item belongs to one MinistryArea (`ministry_area`)
- **ManyToOne**: An Item has one User who created it (`created_by`)
- **ManyToOne**: An Item has one User who last updated it (`last_updated_by`)
- **OneToMany**: An Item can have multiple InventoryTransactions (`transactions`)
- **OneToMany**: An Item can have multiple Maintenance records (`maintenance_records`)
- **OneToMany**: An Item can have multiple Checkout records (`checkouts`)

### InventoryTransaction Model

Tracks all changes to inventory quantities:

- **ManyToOne**: A Transaction belongs to one Item (`item`)
- **ManyToOne**: A Transaction can be from one MinistryArea (`from_ministry`)
- **ManyToOne**: A Transaction can be to one MinistryArea (`to_ministry`)
- **ManyToOne**: A Transaction is conducted by one User (`conducted_by`)

### Maintenance Model

Tracks service and maintenance of inventory items:

- **ManyToOne**: A Maintenance record belongs to one Item (`item`)
- **ManyToOne**: A Maintenance can be supervised by one User (`internal_staff`)

### ItemCheckout Model

Tracks temporary loans of inventory items:

- **ManyToOne**: A Checkout belongs to one Item (`item`)
- **ManyToOne**: A Checkout is checked out by one User (`checked_out_by`)

## Field Definitions

### User Model

| Field         | Type          | Description                           |
| ------------- | ------------- | ------------------------------------- |
| username      | CharField     | Unique username for identification    |
| email         | EmailField    | Unique email address, used for login  |
| password      | CharField     | Encrypted password                    |
| first_name    | CharField     | User's first name                     |
| last_name     | CharField     | User's last name                      |
| role          | CharField     | Role: ADMIN, STAFF, or VOLUNTEER      |
| phone_number  | CharField     | Optional contact phone number         |
| ministry_area | ForeignKey    | Primary ministry area user belongs to |
| bio           | TextField     | Optional biographical information     |
| date_joined   | DateTimeField | When user account was created         |
| last_updated  | DateTimeField | When user profile was last updated    |

### MinistryArea Model

| Field       | Type          | Description                          |
| ----------- | ------------- | ------------------------------------ |
| name        | CharField     | Name of the ministry                 |
| slug        | SlugField     | URL-friendly identifier              |
| description | TextField     | Detailed description of the ministry |
| location    | CharField     | Physical location within the church  |
| leader      | ForeignKey    | User who leads this ministry         |
| active      | BooleanField  | Whether ministry is currently active |
| notes       | TextField     | Additional notes about the ministry  |
| created_at  | DateTimeField | When record was created              |
| updated_at  | DateTimeField | When record was last updated         |

### Category Model

| Field       | Type       | Description                              |
| ----------- | ---------- | ---------------------------------------- |
| name        | CharField  | Name of the category                     |
| description | TextField  | Description of items in this category    |
| parent      | ForeignKey | Optional parent category (for hierarchy) |

### Item Model

| Field            | Type            | Description                        |
| ---------------- | --------------- | ---------------------------------- |
| name             | CharField       | Name of the item                   |
| description      | TextField       | Detailed description               |
| category         | ForeignKey      | Category classification            |
| ministry_area    | ForeignKey      | Ministry area that owns the item   |
| quantity         | PositiveInteger | Current quantity in inventory      |
| min_quantity     | PositiveInteger | Minimum quantity before reordering |
| unit_value       | DecimalField    | Value per unit in dollars          |
| acquisition_date | DateField       | When the item was acquired         |
| condition        | CharField       | Current condition (NEW to DAMAGED) |
| location         | CharField       | Storage location within church     |
| barcode          | CharField       | Unique barcode identifier          |
| image            | ImageField      | Optional photo of the item         |
| notes            | TextField       | Additional notes                   |
| created_by       | ForeignKey      | User who created the record        |
| last_updated_by  | ForeignKey      | User who last updated the record   |
| created_at       | DateTimeField   | When record was created            |
| updated_at       | DateTimeField   | When record was last updated       |

### InventoryTransaction Model

| Field             | Type            | Description                             |
| ----------------- | --------------- | --------------------------------------- |
| item              | ForeignKey      | Item being transacted                   |
| transaction_type  | CharField       | Type: ADD, REMOVE, ADJUST, TRANSFER     |
| quantity          | IntegerField    | Quantity changed (positive or negative) |
| previous_quantity | PositiveInteger | Quantity before transaction             |
| new_quantity      | PositiveInteger | Quantity after                          |
