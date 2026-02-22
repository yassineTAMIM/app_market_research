-- models/marts/dim_apps.sql
-- One row per app, with foreign keys to dim_developers and dim_categories.

{{ config(materialized='table') }}

with apps as (
    select * from {{ ref('stg_apps') }}
),

categories as (
    select category_key, category_name from {{ ref('dim_categories') }}
),

devs as (
    -- Only current developer records for the FK
    select developer_key, developer_name
    from {{ ref('dim_developers') }}
    where is_current = true
)

select
    md5(a.app_id)       as app_key,          -- surrogate key
    a.app_id,                                -- natural key (kept for tracing)
    a.app_name,
    d.developer_key,
    c.category_key,
    a.price,
    a.is_paid,
    a.installs,
    a.catalog_rating,
    a.ratings_count,
    a._loaded_at        as updated_at

from apps a
left join categories c on a.category_name = c.category_name
left join devs       d on a.developer_name = d.developer_name