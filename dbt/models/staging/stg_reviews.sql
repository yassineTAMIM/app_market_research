-- models/staging/stg_reviews.sql
{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'apps_reviews') }}
),

normalized as (
    select
        -- reviewId is the column name from your Lab 1 pipeline
        try_cast("reviewId" as varchar)                     as review_id,
        try_cast("app_id"   as varchar)                     as app_id,
        try_cast("score"    as integer)                     as rating,
        coalesce("content", '')                             as review_text,
        coalesce(try_cast("thumbsUpCount" as integer), 0)  as thumbs_up_count,
        -- "at" is stored as a string like "2025-01-15 10:30:00" from Lab 1
        try_cast("at" as timestamp)                         as reviewed_at,
        coalesce("userName", 'Anonymous')                   as user_name,
        _loaded_at,
        _source_file
    from source
),

validated as (
    select *
    from normalized
    where review_id   is not null
      and app_id      is not null
      and rating      between 1 and 5
      and reviewed_at is not null
      and reviewed_at >= '2015-01-01'
),

deduped as (
    select *,
           row_number() over (partition by review_id order by _loaded_at asc) as rn
    from validated
)

select
    review_id,
    app_id,
    rating,
    review_text,
    thumbs_up_count,
    reviewed_at,
    user_name,
    _loaded_at,
    _source_file
from deduped
where rn = 1