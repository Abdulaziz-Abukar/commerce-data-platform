with src as (
    select
        product_id,
        batch_date,
        source,
        extracted_at,
        loaded_at,
        payload_hash,
        payload
    from {{ source('raw', 'products') }}
),

final as (
    select
        product_id,
        batch_date,

        -- extract from JSON payload
        cast(json_value(payload, '$.title') as string) as product_name,
        cast(json_value(payload, '$.sku') as string) as sku,
        cast(json_value(payload, '$.brand') as string) as brand,
        cast(json_value(payload, '$.category') as string) as category,

        cast(json_value(payload, '$.price') as numeric) as price,
        cast(json_value(payload, '$.discountPercentage') as numeric) as discount_percentage,
        cast(json_value(payload, '$.rating') as numeric) as rating,
        cast(json_value(payload, '$.stock') as int64) as stock,
        
        -- keep lineage meatdata
        source,
        extracted_at,
        loaded_at,
        payload_hash
    from src
)

select * from final