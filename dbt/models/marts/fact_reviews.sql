-- models/marts/fact_reviews.sql
-- Central fact table: one row per review.
--
-- INCREMENTAL LOADING:
--   First run  : full load (the if is_incremental block is skipped)
--   Later runs : only rows where _loaded_at > MAX(_loaded_at) already in the table
--
-- unique_key='review_id' + delete+insert strategy = idempotent:
--   if the same review_id appears in two batches, the old row is replaced, never duplicated.

{{
    config(
        materialized='incremental',
        unique_key='review_id',
        on_schema_change='sync_all_columns',
        incremental_strategy='delete+insert'
    )
}}

with reviews as (
    select * from {{ ref('stg_reviews') }}

    -- INCREMENTAL FILTER: only new rows since last run
    {% if is_incremental() %}
        where _loaded_at > (select max(_loaded_at) from {{ this }})
    {% endif %}
),

apps as (
    select app_key, app_id, developer_key
    from {{ ref('dim_apps') }}
),

dates as (
    select date_key, date
    from {{ ref('dim_date') }}
),

joined as (
    select
        r.review_id,

        -- Foreign keys
        a.app_key,
        a.developer_key,
        cast(strftime(r.reviewed_at::date, '%Y%m%d') as integer) as date_key,

        -- Measures
        r.rating,
        r.thumbs_up_count,

        -- Degenerate dims (no join needed for common queries)
        r.review_text,
        r.user_name,

        -- Audit
        r._loaded_at,
        r._source_file

    from reviews r
    inner join apps  a on r.app_id = a.app_id       -- drops reviews for unknown apps
    inner join dates d on cast(strftime(r.reviewed_at::date, '%Y%m%d') as integer) = d.date_key
),

-- Final safety dedup (handles edge cases where batches overlap)
deduped as (
    select *,
           row_number() over (partition by review_id order by _loaded_at asc) as rn
    from joined
)

select
    review_id,
    app_key,
    developer_key,
    date_key,
    rating,
    thumbs_up_count,
    review_text,
    user_name,
    _loaded_at,
    _source_file
from deduped
where rn = 1