SELECT
  client_id,
  -- Coalesce is more robust here in case we start using a clients dimension as our main reference
  -- This way, we still display their total purchase amount as 0 instead of NULL (which wouldn't be the case with a simple "ELSE 0" statement, as there would be no rows to sum over)
  COALESCE(SUM(CASE WHEN product_type = "MEUBLE" THEN prod_price * prod_qty END),0) AS ventes_meuble,
  COALESCE(SUM(CASE WHEN product_type = "DECO"   THEN prod_price * prod_qty END),0) AS ventes_deco
FROM
  `sandbox-460513.retail.transactions` AS t
LEFT JOIN
  `sandbox-460513.retail.product_nomenclature` AS pn ON t.prop_id = pn.product_id
WHERE
  EXTRACT(YEAR FROM t.date) = 2019
GROUP BY
  t.client_id;