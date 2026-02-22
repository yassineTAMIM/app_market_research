{% snapshot scd2_developers %}

{{
    config(
        target_schema='snapshots',
        unique_key='developer_name',
        strategy='check',
        check_cols=['developer_name'],
        invalidate_hard_deletes=True
    )
}}

-- Reads directly from the raw source (NOT ref) because staging views
-- don't exist yet when `dbt snapshot` runs — it runs before `dbt build`.
-- On first run: every developer gets one open-ended row (dbt_valid_to = NULL).
-- On future runs: if a name changes, old row is closed and a new one opens.

select distinct
    trim(coalesce(developer, 'Unknown'))  as developer_name,
    _loaded_at                            as updated_at
from {{ source('raw', 'apps_catalog') }}
where developer is not null
  and trim(developer) != ''

{% endsnapshot %}