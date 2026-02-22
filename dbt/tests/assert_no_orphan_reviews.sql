-- Fails if any review in fact_reviews has no matching app in dim_apps
select fr.review_id, fr.app_key
from {{ ref('fact_reviews') }} fr
left join {{ ref('dim_apps') }} da on fr.app_key = da.app_key
where da.app_key is null