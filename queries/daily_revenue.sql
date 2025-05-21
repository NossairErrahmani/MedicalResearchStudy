-- Given that the question was ambiguous as to whether the sales-less dates were to be highlighted as well, I came up with 2 solutions :

-- Option 1 : only the dates we have sales for
SELECT
  date,
  SUM(prod_price * prod_qty) AS ventes -- column name is in french as per the sample result
FROM
  `sandbox-460513.retail.transactions` AS t
WHERE
  EXTRACT(YEAR FROM date) = 2019
GROUP BY
  date;

-- Option 2 : every date for our range
WITH Dates2019 AS (
  -- We first generate a series of all dates in 2019
  SELECT date
  FROM UNNEST(GENERATE_DATE_ARRAY('2019-01-01', '2019-12-31', INTERVAL 1 DAY)) AS date
),
DailySales AS (
  SELECT
    date AS sale_date,
    SUM(prod_price * prod_qty) AS sale_revenue
  FROM
    `sandbox-460513.retail.transactions`
  WHERE
    EXTRACT(YEAR FROM date) = 2019
  GROUP BY
    date
)
SELECT
  ds.date,
  COALESCE(s.sale_revenue, 0) AS ventes -- If no sales for a date, sale_revenue will be NULL, so we'll replace with 0
FROM
  Dates2019 ds
LEFT JOIN
  DailySales s ON ds.date = s.sale_date
ORDER BY
  ds.date;
