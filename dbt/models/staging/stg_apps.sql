-- models/staging/stg_apps.sql
-- Cleans your apps_catalog data: normalizes types, fills nulls, deduplicates.
-- Materialized as a VIEW so it always reflects the latest raw data.

{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'apps_catalog') }}
),

cleaned as (
    select
        trim(appId)                                                       as app_id,
        trim(title)                                                       as app_name,
        trim(coalesce(developer, 'Unknown'))                              as developer_name,

        -- score is already clean from your Lab 1 pipeline
        try_cast(score as double)                                         as catalog_rating,
        try_cast(ratings as integer)                                      as ratings_count,

        -- installs: "1,000,000+" → 1000000
        try_cast(
            regexp_replace(cast(installs as varchar), '[^0-9]', '', 'g')
            as bigint
        )                                                                 as installs,

        trim(coalesce(genre, 'Unknown'))                                  as category_name,

        -- price: already 0.0 or numeric from Lab 1
        coalesce(try_cast(price as double), 0.0)                         as price,

        case when coalesce(try_cast(price as double), 0) > 0
             then true else false end                                      as is_paid,

        _loaded_at

    from source
    where appId is not null
),

deduped as (
    select *,
           row_number() over (partition by app_id order by _loaded_at desc) as rn
    from cleaned
)

select
    app_id,
    app_name,
    developer_name,
    catalog_rating,
    ratings_count,
    installs,
    category_name,
    price,
    is_paid,
    _loaded_at
from deduped
where rn = 1