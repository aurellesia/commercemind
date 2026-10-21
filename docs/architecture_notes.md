# CommerceMind Architecture Notes

## Project Identity

**CommerceMind** is a learning-driven ecommerce platform that starts as a clean CRUD system and grows into an intelligent commerce platform with analytics and a Decision Engine.

The project is not only a storefront. It is a technical learning ground for building ecommerce capabilities in deliberate stages: catalog, inventory, customers, orders, payments, fulfillment, analytics, and eventually decision automation.

## Product Direction

CommerceMind is positioned as:

> A modular ecommerce platform that turns operational commerce data into better business decisions.

The long-term direction is to move from **recording commerce activity** to **reasoning about commerce activity**.

Future business questions the platform should answer:

- Which products should be restocked?
- Which products are underperforming?
- Which customers are likely to buy again?
- Which discounts or bundles make sense?
- Which operational decisions should be recommended automatically?

Every intelligent feature must be grounded in reliable commerce data. The system should not add AI or recommendation features before the operational model is trustworthy.

## Default Brand Policy

CommerceMind is also the default brand for the local/demo installation.

- Default brand name: `CommerceMind`
- Default brand slug: `default`
- Default brand id: `1`
- Legacy admin routes under `/admin/*` are treated as temporary CommerceMind default-brand panels.
- Brand-scoped merchant admin routes under `/brands/{brandSlug}/admin/*` are the long-term direction.
- Until each legacy admin panel is fully ported, links from brand-scoped placeholders to `/admin/*` intentionally open CommerceMind demo/default data.
- New brand-scoped work should prefer explicit `brand_id` or `brand_slug` and should not silently mutate non-default brand data through legacy routes.

## Current Architecture

The current project is a **modular monolith ecommerce app**.

```text
ecommerce/
├── backend/                 FastAPI, SQLAlchemy, Pydantic
├── frontend/                SvelteKit, TypeScript, Tailwind CSS
├── docs/                    architecture notes and implementation backlog
├── docker-compose.yml       local PostgreSQL service
└── README.md
```

The project is intentionally not split into microservices. Domain boundaries are visible in the codebase, but all backend modules still run inside one FastAPI application and one PostgreSQL database.

## Runtime Components

### Backend

Backend entry point:

```text
backend/main.py
```

Responsibilities:

- Create the FastAPI app.
- Configure CORS for the local SvelteKit frontend.
- Register API routers.
- Create SQLAlchemy tables on startup for the current local-development phase.

Current backend stack:

- FastAPI for HTTP API.
- SQLAlchemy for ORM models and database access.
- Pydantic for request and response schemas.
- PostgreSQL as the database.

Database configuration:

```text
backend/database.py
```

Default local connection:

```text
postgresql://myuser:mypassword@localhost:5432/mydb
```

Local PostgreSQL is defined in:

```text
docker-compose.yml
```

### Frontend

Frontend app:

```text
frontend/
```

Current frontend stack:

- SvelteKit
- TypeScript
- Tailwind CSS
- lucide-svelte
- local UI components for button, card, badge, and input

Route areas:

```text
/
/admin
/admin/products
/admin/inventory
/admin/customers
/admin/orders
/admin/payments
/storefront
/storefront/products
```

The admin area is the most developed frontend surface. Product management already supports listing, searching, creating, editing, deleting, toast feedback, and modal workflows.

The storefront currently exists as a placeholder and should grow after the core backend workflow becomes more reliable.

## Backend Layering

The backend currently follows this flow:

```text
API route -> CRUD layer -> SQLAlchemy model -> PostgreSQL
              ^
              |
        Pydantic schema
```

Current layer responsibilities:

- `backend/api/`: HTTP route handlers, request validation glue, API errors.
- `backend/crud/`: database operations and simple table-level workflows.
- `backend/models/`: SQLAlchemy table definitions and relationships.
- `backend/schema_models/`: Pydantic request and response models.
- `backend/schemas.py`: compatibility export layer for schema models.
- `backend/database.py`: engine, session factory, and database dependency.

As workflows become more domain-heavy, routes should stay thin and delegate to service modules. CRUD modules are acceptable for simple master data, but lifecycle behavior such as reservation, cancellation, payment outcome, and fulfillment should live in service-layer functions.

## Domain Boundaries

Current backend domains:

```text
Catalog
- Product

Inventory
- InventoryItem
- InventoryReservation
- InventoryMovement

Customer
- Customer

Order
- Order
- OrderItem

Payment
- Payment

Pricing
- PriceSet
- PriceSetItem
- Channel
- Region
```

Expected future domains:

```text
Fulfillment
- shipment/fulfillment state
- stock deduction trigger

Returns
- return intake
- restock decision

Decision Engine
- rules
- signals
- recommendations
- decision history
```

## Database Relationship Summary

Current core relationships:

```text
products 1 -> 1 inventory_items
products 1 -> many price_sets
price_sets 1 -> many price_set_items
channels 1 -> many price_set_items
regions 1 -> many price_set_items

customers 1 -> many orders
orders 1 -> many order_items
products 1 -> many order_items
orders 1 -> 1 payments

products 1 -> many inventory_reservations
orders 1 -> many inventory_reservations
order_items 1 -> many inventory_reservations
products 1 -> many inventory_movements
```

## Catalog

The `products` table represents sellable catalog items.

```text
products
- id: integer, primary key
- name: string, required, indexed
- description: text, nullable
- base_price: numeric, required
- status: string, required, default draft at database level
- created_at: datetime, required
- updated_at: datetime, required
```

Allowed product statuses:

```text
draft
active
archived
discontinued
```

Rules:

- `base_price` is the fallback price before channel, region, or price-set rules are applied.
- Money fields use fixed precision numeric values.
- Product status should represent lifecycle without deleting historical order data.
- Hard deletion should be avoided once products are referenced by orders.

## Pricing

Pricing is already separated from the base catalog model.

```text
price_sets
- id
- product_id
- name
- starts_at
- ends_at
- is_active
- created_at
- updated_at

price_set_items
- id
- price_set_id
- channel_id
- region_id
- price
- currency
- priority
- is_active
- created_at
- updated_at
```

Pricing direction:

- `Product.base_price` remains the fallback.
- `PriceSet` groups alternative prices.
- `PriceSetItem` can target channel and region.
- Priority allows the system to choose between multiple matching prices later.

## Inventory

Inventory is transitioning from simple CRUD into a real ecommerce domain.

### Inventory Aggregate

The `inventory_items` table stores the current stock aggregate for each product.

```text
inventory_items
- id: integer, primary key
- product_id: integer, required, foreign key -> products.id, unique
- on_hand_quantity: integer, required, default 0
- reserved_quantity: integer, required, default 0
- low_stock_threshold: integer, required, default 0
- created_at: datetime, required
- updated_at: datetime, required
```

Derived value:

```text
available_quantity = on_hand_quantity - reserved_quantity
```

Rules:

- One product has one inventory aggregate for now.
- `on_hand_quantity` means stock physically or logically held by the store.
- `reserved_quantity` means stock currently attached to active reservations.
- `available_quantity` means stock still available to sell.
- `on_hand_quantity` must never be negative.
- `reserved_quantity` must never be negative.
- `reserved_quantity` must never exceed `on_hand_quantity`.

### Inventory Reservations

The `inventory_reservations` table records stock held for an order or order item.

```text
inventory_reservations
- id
- product_id
- order_id
- order_item_id
- quantity
- status
- expires_at
- created_at
- updated_at
```

Allowed reservation statuses:

```text
active
released
committed
expired
```

Rules:

- Reservation quantity must be greater than zero.
- Active reservations increase `InventoryItem.reserved_quantity`.
- Released or expired reservations should decrease `reserved_quantity`.
- Committed reservations represent stock that has moved out through fulfillment.
- Reservation records should allow precise release or commit per order.

### Inventory Movements

The `inventory_movements` table is the audit ledger for stock changes.

```text
inventory_movements
- id
- product_id
- quantity
- movement_type
- reference_type
- reference_id
- notes
- created_at
- updated_at
```

Allowed movement types:

```text
inbound
reservation
release
deduction
adjustment
return
```

Rules:

- Movement quantity must be greater than zero.
- Every domain stock action should create a movement row.
- `reference_type` and `reference_id` should point to the business reason when possible.
- The movement ledger is for audit and observability; the aggregate remains in `inventory_items`.

## Customers

The `customers` table represents buyers.

```text
customers
- id: integer, primary key
- name: string, required
- email: string, required, unique, indexed
- phone: string, nullable
- address: text, nullable
- created_at: datetime, required
- updated_at: datetime, required
```

Rules:

- Email is unique in the current single-store phase.
- Address is stored directly on the customer for now.
- A future version should support multiple addresses per customer.

## Orders

The `orders` table represents purchase intent and commercial transaction state.

```text
orders
- id: integer, primary key
- customer_id: integer, required, foreign key -> customers.id
- status: string, required, indexed
- total_amount: numeric, required, default 0
- created_at: datetime, required
- updated_at: datetime, required
```

Current order statuses:

```text
pending
awaiting_payment
paid
processing
fulfilled
completed
cancelled
```

Current behavior:

- Creating an order validates that the customer exists.
- Creating an order validates that each product exists.
- `total_amount` is calculated from order item subtotals.
- Creating an order reserves inventory and moves the order to `awaiting_payment`.
- Cancelling an order releases active inventory reservations.
- Payment `paid` moves the order to `paid` without deducting physical stock.
- Fulfillment moves the order to `fulfilled` and deducts physical stock.

Target behavior:

- Order status changes should move through workflow functions, not direct field updates.
- A future fulfillment model can split shipment state from order state when the workflow needs more detail.

## Order Items

The `order_items` table stores products purchased inside an order.

```text
order_items
- id: integer, primary key
- order_id: integer, required, foreign key -> orders.id
- product_id: integer, required, foreign key -> products.id
- quantity: integer, required
- unit_price: numeric, required
- subtotal: numeric, required
- created_at: datetime, required
- updated_at: datetime, required
```

Rules:

- `quantity` must be greater than zero.
- `unit_price` should copy the selected product price at the time of purchase.
- `subtotal` must equal `quantity * unit_price`.
- Order history must not change if the product price changes later.

## Payments

The `payments` table stores payment records for orders.

```text
payments
- id: integer, primary key
- order_id: integer, required, foreign key -> orders.id, unique
- status: string, required, indexed
- method: string, required
- amount: numeric, required
- paid_at: datetime, nullable
- created_at: datetime, required
- updated_at: datetime, required
```

Current payment statuses:

```text
pending
paid
failed
refunded
```

Current payment methods:

```text
manual
bank_transfer
cash
```

Current behavior:

- One order can have one payment record.
- Marking a payment as `paid` sets `paid_at` when it is still empty.
- Payment `paid` moves the order to `paid` without deducting physical stock.
- Payment `failed` releases active reservation and cancels the order.
- Payment `refunded` does not restock inventory.

Target behavior:

- Restock should happen through a separate return/receiving process.

## Ecommerce Lifecycle Target

The target lifecycle separates payment, reservation, fulfillment, refund, and return.

```text
order create
-> validate available stock
-> create order and order items
-> create active reservations
-> increase reserved_quantity
-> create reservation movements

order cancel
-> release active reservations
-> decrease reserved_quantity
-> create release movements
-> mark order cancelled

payment paid
-> mark payment paid
-> set paid_at
-> move order to paid
-> do not deduct on_hand_quantity yet

payment failed
-> mark payment failed
-> release active reservations
-> mark order cancelled

fulfillment/shipping
-> commit active reservations
-> decrease reserved_quantity
-> decrease on_hand_quantity
-> create deduction movements

refund
-> mark payment refunded
-> do not restock automatically

return received
-> receive stock back if item is resellable
-> increase on_hand_quantity
-> create return movement
```

This lifecycle is tracked in more detail in:

```text
docs/todo_inventory_architecture.md
```

## API Surface

Current registered backend routers:

```text
/products
/inventory-items
/customers
/orders
/order-items
/payments
```

Current API style:

- Master data uses normal CRUD routes.
- Orders expose creation, read, update, status update, cancel, and delete routes.
- Payments expose creation, read, update, status update, and delete routes.
- Inventory still exposes aggregate item CRUD.

Target API style:

- Keep simple CRUD for master data such as products, customers, regions, and channels.
- Add action-based inventory endpoints for domain commands:
  - receive stock
  - adjust stock
  - reserve stock
  - release reservation
  - commit reservation
- Avoid making manual stock number edits the main business path.

## Frontend Architecture

Frontend route layout:

```text
frontend/src/routes/
├── +page.svelte                 application area selector
├── admin/
│   ├── +layout.svelte           admin shell and navigation
│   ├── +page.svelte             dashboard overview
│   ├── products/+page.svelte    product management
│   ├── inventory/+page.svelte
│   ├── customers/+page.svelte
│   ├── orders/+page.svelte
│   └── payments/+page.svelte
└── storefront/
    ├── +layout.svelte
    ├── +page.svelte
    └── products/+page.svelte
```

Frontend library layout:

```text
frontend/src/lib/
├── api/                         API clients
├── components/ui/               shared UI primitives
├── admin/                       admin-specific helpers, currently minimal
├── storefront/                  storefront-specific helpers, currently minimal
└── utils.ts
```

Current frontend state:

- Admin navigation is established.
- Admin products is the most complete workflow.
- Other admin pages and storefront pages should grow after backend workflows stabilize.

## Service Layer Direction

The next major backend architectural move is adding service functions for business workflows.

Recommended near-term service module:

```text
backend/crud/inventory_service.py
```

Initial service functions:

```text
receive_stock(product_id, quantity, reference, notes)
adjust_stock(product_id, delta, reference, notes)
reserve_stock_for_order(order_id)
release_stock_for_order(order_id, reason)
commit_stock_for_order(order_id)
```

Each service function should:

- Update the inventory aggregate.
- Create reservations when relevant.
- Create inventory movement rows.
- Preserve stock invariants.
- Fail if stock is not sufficient.
- Run inside a transaction so partial workflow updates do not persist.

Over time, service modules can move from `backend/crud/` into clearer domain folders, for example:

```text
backend/inventory/service.py
backend/orders/service.py
backend/payments/service.py
```

That migration should happen when the workflow logic is substantial enough to justify the new package boundary.

## Engineering Principles

CommerceMind should be built with these principles:

- **Simple first, modular early**: avoid premature microservices, but keep domain boundaries visible.
- **Data correctness before intelligence**: recommendations are only useful if source data is trustworthy.
- **Business logic belongs outside routes**: API routes should stay thin as workflows grow.
- **CRUD is fine for master data**: but transaction workflows need service-layer orchestration.
- **Schema changes should be deliberate**: introduce migrations before the data model becomes important.
- **Tests should follow risk**: prioritize inventory invariants, order lifecycle, payment behavior, and API contracts.
- **Every abstraction must earn its place**: add layers when they reduce real complexity.

## Current Gaps

Known architecture gaps:

- Storefront pages are still mostly placeholders.
- Admin inventory/order/payment pages still need UI work for the backend workflows that now exist.
- Return handling is currently represented by receive-stock commands with return references; a richer returns domain can be added later.

## Near-Term Roadmap

Recommended implementation order:

1. Expand admin inventory, orders, and payments pages around the domain command endpoints.
2. Build storefront product browsing on top of active products and available inventory.
3. Add a dedicated returns domain if return intake needs inspection, disposition, or non-restock outcomes.
4. Introduce the first rule-based Decision Engine only after enough operational data exists.

## Decision Engine Definition

The Decision Engine is the future intelligence layer of CommerceMind.

Its job is to produce recommendations or decisions from commerce data. Early versions should be rule-based. Later versions can use scoring, statistical signals, or model-assisted decisions.

Example early decisions:

- Recommend restocking when stock falls below a threshold.
- Flag products with low sales and high inventory.
- Suggest discount candidates based on age, stock, and sales velocity.
- Rank best-selling products over a time period.

The Decision Engine should store decision outputs so the system can explain what it recommended and why.

The Decision Engine should sit on top of reliable commerce workflows. It should not become a substitute for correct catalog, inventory, order, payment, fulfillment, and return data.

## Non-Goals For Now

CommerceMind should not prioritize these yet:

- Microservices.
- Distributed event streaming.
- Complex AI features without reliable commerce data.
- Payment gateway integration before the order model is stable.
- Marketplace or multi-tenant complexity before the single-store domain is solid.
- Promotion engines before pricing, inventory, and order lifecycle are reliable.

These may become valid later, but they are not the right early constraints.
