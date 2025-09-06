# Queries

## Main table

``` sql
SELECT prices.id, perfums.name as perfum, merchants.name as merchant, prices.ts, CAST(prices.price as float) / 100 as price 
FROM prices 
JOIN perfums ON prices.perfum_id == perfums.id 
JOIN merchants ON prices.merchant_id == merchants.id 
ORDER BY perfums.name, price;
```

