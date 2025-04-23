# Church Inventory Management System - Model Relationships

This document outlines the data model for the Church Inventory Management System, explaining the core entities and their relationships.

## Core Entities

### 1. User

The `User` model extends Django's built-in `AbstractUser` to add role-based authentication:

- **Fields:**

  - Standard Django user fields (username, email, password, etc.)
  - `role`: Enum field with options ADMIN, STAFF, VOLUNTEER
  - `phone_number`: Optional contact number
  - `ministry_area`: Foreign key to MinistryArea (optional)
  - `bio`: Text field for user information

- **Relationships:**
  - One-to-Many with MinistryArea (as leader)
  - One-to-Many with Item (as creator and updater)
  - One-to-Many with InventoryTransaction (as conductor)

### 2. Ministry Area

The `MinistryArea` model represents different departments or ministry teams within the church:

- **Fields:**

  - `name`: Name of the ministry
  - `slug`: URL-friendly version of name
  - `description`: Detailed description
  - `location`: Physical location in the church
  - `leader`: Foreign key to User (optional)
  - `active`: Boolean indicating if ministry is active
  - `notes`: Additional information

- **Relationships:**
  - Many-to-One with User (as leader)
  - One-to-Many with Item (items belonging to ministry)
  - One-to-Many with User (members of ministry)

### 3. Category

The `Category` model provides a hierarchical classification system for inventory items:

- **Fields:**

  - `name`: Category name
  - `description`: Category description
  - `parent`: Self-referential foreign key for hierarchical categories

- **Relationships:**
  - Self-referential for parent-child relationships
  - One-to-Many with Item

### 4. Item

The `Item` model is the central entity representing inventory items:

- **Fields:**

  - `name`: Item name
  - `description`: Detailed description
  - `category`: Foreign key to Category
  - `ministry_area`: Foreign key to MinistryArea
  - `quantity`: Current inventory count
  - `min_quantity`: Reorder threshold
  - `unit_value`: Monetary value per unit
  - `acquisition_date`: Date when acquired
  - `condition`: Enum (NEW, EXCELLENT, GOOD, FAIR, POOR, DAMAGED)
  - `location`: Storage location
  - `barcode`: Unique identifier (optional)
  - `image`: Product image (optional)
  - `notes`: Additional information
  - `created_by`/`last_updated_by`: Foreign keys to User

- **Relationships:**
  - Many-to-One with Category
  - Many-to-One with MinistryArea
  - Many-to-One with User (creator)
  - Many-to-One with User (updater)
  - One-to-Many with InventoryTransaction
  - One-to-Many with Maintenance
  - One-to-Many with ItemCheckout

### 5. Inventory Transaction

The `InventoryTransaction` model tracks all inventory changes:

- **Fields:**

  - `item`: Foreign key to Item
  - `transaction_type`: Enum (ADDITION, REMOVAL, ADJUSTMENT, TRANSFER)
  - `quantity`: Amount changed
  - `previous_quantity`: Quantity before transaction
  - `new_quantity`: Quantity after transaction
  - `from_ministry`/`to_ministry`: Foreign keys to MinistryArea (for transfers)
  - `reason`: Explanation for transaction
  - `conducted_by`: Foreign key to User
  - `transaction_date`: When transaction occurred

- **Relationships:**
  - Many-to-One with Item
  - Many-to-One with User (conductor)
  - Many-to-One with MinistryArea (from/to)

### 6. Maintenance

The `Maintenance` model tracks service and maintenance records:

- **Fields:**

  - `item`: Foreign key to Item
  - `maintenance_date`: When maintenance occurred
  - `description`: What was done
  - `cost`: Expense for maintenance
  - `performed_by`: Who performed the maintenance
  - `internal_staff`: Foreign key to User (optional)
  - `next_maintenance_date`: When next service is due

- **Relationships:**
  - Many-to-One with Item
  - Many-to-One with User (supervisor)

### 7. Item Checkout

The `ItemCheckout` model tracks items temporarily loaned out:

- **Fields:**

  - `item`: Foreign key to Item
  - `checked_out_by`: Foreign key to User
  - `checkout_date`: When checked out
  - `due_date`: When due to return
  - `quantity`: Number checked out
  - `purpose`: Reason for checkout
  - `checked_in_date`: When returned (null if still out)

- **Relationships:**
  - Many-to-One with Item
  - Many-to-One with User

## Entity Relationship Diagram (ERD)

```
+-------------+     +----------------+     +------------+
|    User     |     | MinistryArea   |     |  Category  |
+-------------+     +----------------+     +------------+
| id          |     | id             |     | id         |
| username    |     | name           |     | name       |
| email       |     | slug           |     | description|
| password    |     | description    |     | parent     |
| first_name  |     | location       |     +------------+
| last_name   |     | leader         |           |
| role        |     | active         |           |
| phone_number|     | notes          |           |
| ministry    |<----| created_at     |           |
| bio         |     | updated_at     |           |
+-------------+     +----------------+           |
      |                    |                     |
      |                    |                     |
      v                    v                     v
+------------------------------------------+
|               Item                       |
+------------------------------------------+
| id          | unit_value     | notes    |
| name        | acq_date       | created_by|
| description | condition      | updated_by|
| category    | location       | created_at|
| ministry    | barcode        | updated_at|
| quantity    | image          |          |
| min_quantity|                |          |
+------------------------------------------+
      |                |                |
      |                |                |
      v                v                v
+---------------+  +-------------+  +-------------+
| Inventory     |  | Maintenance |  | ItemCheckout|
| Transaction   |  +-------------+  +-------------+
+---------------+  | id          |  | id          |
| id            |  | item        |  | item        |
| item          |  | maint_date  |  | checked_out |
| type          |  | description |  | checkout_date|
| quantity      |  | cost        |  | due_date    |
| prev_quantity |  | performed_by|  | quantity    |
| new_quantity  |  | staff       |  | purpose     |
| from_ministry |  | next_date   |  | checked_in  |
| to_ministry   |  | created_at  |  +-------------+
| reason        |  +-------------+
| conducted_by  |
| transaction_dt|
+---------------+
```

## Key Design Decisions

1. **Role-Based Access Control**: The custom User model with roles provides granular control over permissions.

2. **Hierarchical Categories**: Self-referential relationship allows for nested categories (e.g., "Audio Equipment" > "Microphones").

3. **Ministry-Based Organization**: Items are organized by ministry areas, allowing for departmental inventory management.

4. **Complete Transaction History**: Every inventory change is recorded, providing full audit trail.

5. **Maintenance Tracking**: Separate model for maintenance helps track service history and schedule future maintenance.

6. **Item Checkout System**: Allows tracking of items that are temporarily removed but expected to return.

7. **Audit Fields**: Created/updated timestamps and user references provide accountability.

## Database Constraints and Integrity

1. **Foreign Key Constraints**: Ensure referential integrity between related models.

2. **Cascading Deletes**: Used selectively (e.g., deleting an Item cascades to delete its transactions).

3. **NULL Constraints**: Foreign keys that should allow dissolution of relationships use `SET_NULL` on delete.

4. **Default Values**: Sensible defaults provided where appropriate (e.g., condition, quantity).

5. **Unique Constraints**: Applied to fields like barcode to ensure uniqueness.

6. **Signals**: Used to automatically create transaction records when items are created or modified.
