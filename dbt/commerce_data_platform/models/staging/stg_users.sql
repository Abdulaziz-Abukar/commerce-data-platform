with src as (
    select
        user_id,
        batch_date,
        source,
        extracted_at,
        loaded_at,
        payload_hash,
        payload
    from {{ source('raw', 'users') }}
),

final as (
    select
        user_id,
        batch_date,

        -- extract from JSON payload
        cast(json_value(payload, '$.firstName') as string) as first_name,
        cast(json_value(payload, '$.lastName') as string) as last_name,
        cast(json_value(payload, '$.maidenName') as string) as maiden_name,
        cast(json_value(payload, '$.gender') as string) as gender,
        cast(json_value(payload, '$.email') as string) as email,
        cast(json_value(payload, '$.phone') as string) as phone_number,
        cast(json_value(payload, '$.username') as string) as username,
        cast(json_value(payload, '$.address.address') as string) as address_line,
        cast(json_value(payload, '$.address.city') as string) as city,
        cast(json_value(payload, '$.address.state') as string) as state,
        cast(json_value(payload, '$.address.postalCode') as string) as postal_code,
        cast(json_value(payload, '$.address.country') as string) as country,

        -- keep lineage metadata
        source,
        extracted_at,
        loaded_at,
        payload_hash
    from src
)

select * from final