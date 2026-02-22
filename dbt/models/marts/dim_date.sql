-- models/marts/dim_date.sql
-- Date dimension generated programmatically — no seed file to maintain.
-- Covers all your review dates (Apr 2019 – Feb 2026) plus a future buffer.

{{ config(materialized='table') }}

-- Generate one row per day between 2019-01-01 and 2027-12-31
with date_spine as (
    select
        ('2019-01-01'::date + (n || ' days')::interval)::date as date
    from generate_series(0, 3286) as t(n)
),

with_attributes as (
    select
        cast(strftime(date, '%Y%m%d') as integer)   as date_key,   -- e.g. 20250115
        date,
        extract('year'    from date)::integer        as year,
        extract('month'   from date)::integer        as month,
        extract('quarter' from date)::integer        as quarter,
        extract('isodow'  from date)::integer        as day_of_week, -- 1=Mon 7=Sun
        case when extract('isodow' from date) >= 6
             then true else false end                as is_weekend,
        strftime(date, '%B')                        as month_name,   -- January
        strftime(date, '%A')                        as day_name,     -- Monday
        strftime(date, '%Y-%m')                     as year_month    -- 2025-01
    from date_spine
)

select * from with_attributes
order by date_key