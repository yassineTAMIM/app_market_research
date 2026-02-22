-- models/marts/dim_categories.sql
-- One row per unique app category.
-- Type-1 (no history needed — categories don't change).

{{ config(materialized='table') }}

with categories as (
    select distinct category_name
    from {{ ref('stg_apps') }}
    where category_name is not null
)

select
    md5(category_name)  as category_key,   -- surrogate key
    category_name
from categories
order by category_name