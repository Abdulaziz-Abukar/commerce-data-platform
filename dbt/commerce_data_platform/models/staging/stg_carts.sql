with src as (
    select
        cart_id,
        batch_date,
        source,
        extracted_at,
        loaded_at,
        payload_hash,
        payload
    from {{ source('raw', 'carts')}}
),

final as (
    select
        cart_id,
        batch_date,

        -- extract from JSON payload
        cast(json_value(payload, '$.userId') as int64) as user_id,
        
        cast(json_value(payload, '$.total') as numeric) as total_amount,
        cast(json_value(payload, '$.discountedTotal') as numeric) as discounted_total,
        cast(json_value(payload, '$.totalProducts') as int64) as total_products,
        cast(json_value(payload, '$.totalQuantity') as int64) as total_quantity,

        -- keep lineage meatdata
        source,
        extracted_at,
        loaded_at,
        payload_hash
    from src
)

select * from final