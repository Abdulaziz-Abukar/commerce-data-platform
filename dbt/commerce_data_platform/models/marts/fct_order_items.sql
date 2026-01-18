-- models/marts/fact_order_items.sql
with items as (
    select *
    from {{ ref('stg_cart_items') }}
),
users as (
    select user_id, user_key
    from {{ ref('dim_user') }}
),
products as (
    select product_id, product_key
    from {{ ref('dim_product') }}
),
dates as (
    select date, date_key
    from {{ ref('dim_date') }}
)

select
    -- Surrogate key
    to_hex(sha256(concat(cast(items.order_id as string), '-', cast(items.product_id as string)))) as order_item_id,

    items.order_id,

    users.user_key,
    products.product_key,
    dates.date_key,

    items.snapshot_date,
    items.quantity,
    items.price,
    items.item_total,
    items.discount_percentage,
    items.discount_total

from items
left join users on items.user_id = users.user_id
left join products on items.product_id = products.product_id
left join dates on date(items.snapshot_date) = dates.date