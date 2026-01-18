with src as (
    select
        cart_id,
        batch_date,
        source,
        extracted_at,
        loaded_at,
        payload_hash,
        payload
    from {{ source('raw', 'carts') }}
),

exploded as (
    select 
        cart_id as order_id,
        batch_date,
        cast(json_value(payload, '$.userId') as int64) as user_id,

        -- each item in products[]
        item
    from src,
    unnest(json_query_array(payload, '$.products')) as item
),

final as (
    select
        order_id,
        batch_date,
        user_id,

        safe_cast(json_value(item, '$.id') as int64) as product_id,
        safe_cast(json_value(item, '$.quantity') as int64) as quantity,
        safe_cast(json_value(item, '$.price') as numeric) as price,
        safe_cast(json_value(item, '$.total') as numeric) as item_total,
        safe_cast(json_value(item, '$.discountPercentage') as numeric) as discount_percentage,
        safe_cast(json_value(item, '$.discountedTotal') as numeric) as discount_total
    from exploded
)

select * from final
