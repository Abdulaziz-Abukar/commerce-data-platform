-- models/marts/dim_date.sql
with dates as (
    select d as date
    from unnest(generate_date_array(date('2018-01-01'), date('2026-12-31'))) as d
)
select
    format_date('%Y%m%d', date) as date_key,
    date,
    extract(year from date) as year,
    extract(month from date) as month,
    extract(day from date) as day,
from dates