-- tests/assert_no_data_loss.sql
-- fact_reviews should never have MORE unique review_ids than stg_reviews.
-- If it does, something was deleted upstream and we have ghost rows in the fact table.

select
    (select count(distinct review_id) from {{ ref('fact_reviews') }})  as fact_count,
    (select count(distinct review_id) from {{ ref('stg_reviews') }})   as staging_count
where fact_count > staging_count