-- models/marts/dim_product.sql
with base as (
    select *
    from {{ ref('stg_products') }}
),
dedup as (
    select *,
        row_number() over (partition by product_id order by extracted_at desc) as rn
    from base
)
select
    to_hex(sha256(cast(product_id as string))) as product_key,
    product_id,
    product_name,
    sku,
    brand,
    category,
    price,
    discount_percentage,
    rating,
    stock
from dedup
where rn = 1