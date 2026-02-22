-- tests/assert_rating_distribution_sane.sql
-- Fails if any single star rating makes up >95% of all reviews.
-- Catches silent data quality issues (e.g. all reviews scraped as 5-star).

with counts as (
    select rating, count(*) as n
    from {{ ref('fact_reviews') }}
    group by rating
),
total as (
    select sum(n) as total from counts
)
select
    c.rating,
    round(c.n * 100.0 / t.total, 1) as pct
from counts c cross join total t
where c.n * 100.0 / t.total > 95