<p align="center">
  <img src="static/flaire.webp" alt="flaire" width="350"/>
</p>

# Flaire

Flaire aims to be more than just a scraper; it wants to be a price-monitoring tool for perfumes to detect interesting deals.

## Init

Database creation and initialization

``` sh
alembic upgrade head
```

## Track

Track current prices

``` sh
python -m flaire.track CONTRACT_YAML
```

## Panel

Historic prices viewer

``` sh
streamlit run src/flaire/panel.py CONTRACT_YAML 
```
