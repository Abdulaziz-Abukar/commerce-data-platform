-- models/marts/dim_user.sql
with base as (
    select *
    from {{ ref('stg_users') }}
),
dedup as (
    select *,
        row_number() over (partition by user_id order by extracted_at desc) as rn
    from base
)
select
    to_hex(sha256(cast(user_id as string))) as user_key,
    user_id,
    first_name,
    last_name,
    maiden_name,
    gender,
    email,
    phone_number,
    username,
    address_line,
    city,
    state,
    postal_code,
    country
from dedup
where rn = 1