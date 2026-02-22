-- models/marts/dim_developers.sql
-- Reads from the SCD2 snapshot to expose current + historical developer records.
-- is_current = true → the version valid right now.
-- is_current = false → a historical version (developer was renamed/changed).

{{ config(materialized='table') }}

select
    md5(developer_name)                             as developer_key,
    developer_name,
    dbt_valid_from                                  as valid_from,
    coalesce(dbt_valid_to, '9999-12-31'::timestamp) as valid_to,
    case when dbt_valid_to is null then true
         else false end                             as is_current
from {{ ref('scd2_developers') }}