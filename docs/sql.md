# Queries

## Main table

``` sql
SELECT 
    prices.id, 
    prices.ts, 
    perfums.name as perfum, 
    brands.name as brand, 
    merchants.name as merchant, 
    CAST(prices.price as float) / 100 as price 
FROM prices 
JOIN perfums ON prices.perfum_id == perfums.id
JOIN brands ON perfums.brand_id == brands.id
JOIN merchants ON prices.merchant_id == merchants.id 
ORDER BY perfums.name, price;
```

