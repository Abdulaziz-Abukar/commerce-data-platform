-- models/marts/fct_orders.sql
with carts as (
    select *
    from {{ ref('stg_carts') }}
),
users as (
    select user_id, user_key
    from {{ ref('dim_user') }}
),
dates as (
    select date, date_key
    from {{ ref('dim_date') }}
)

select
    carts.cart_id as order_id,          -- degenerate dimension
    users.user_key,
    dates.date_key,                     -- snapshot date_key

    carts.snapshot_date,                -- keep the human-readable date
    carts.total_amount,
    carts.discounted_total,
    carts.total_products,
    carts.total_quantity

from carts
left join users on carts.user_id = users.user_id
left join dates on date(carts.snapshot_date) = dates.date