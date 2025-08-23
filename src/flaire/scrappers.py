import yaml
import pandas as pd
from botasaurus.browser import browser, Driver
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

def get_soup_from_url(request, url):
    response = request.get(url)
    response.raise_for_status()

    soup = soupify(response)
    return soup


def clean_price_text(text):
    return float(text.replace('€', '').replace(',', '.').replace('\n', '').replace(' ', ''))

def get_price(obj):
    text = obj.get_text()
    return clean_price_text(text)

@request(max_retry=10, run_async=True, close_on_crash=True, output=None)
def scrape_notino_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find(id='pd-price')
    price = get_price(obj)

    return price

@request(max_retry=10, run_async=True, close_on_crash=True, output=None)
def scrape_brasty_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('dl', class_='c-pd-shopbox__row').find('dd')
    price = get_price(obj)

    return price

@request(max_retry=10, run_async=True, close_on_crash=True, output=None)
def scrape_druni_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('span', class_='price').find('span')
    text = obj.contents[0]
    price = clean_price_text(text)

    return price

@browser(
    headless=False,  # Canvia a True si vols que sigui invisible
    block_images=False,
    wait_for_complete_page_load=True,
    close_on_crash=True)
def _scrape_primor_price(driver, data):
    driver.get(data['url'])

    # Haz clic en la opción 125 ml
    driver.click('label', '.swatch-option .product-option-value-label .cursor-pointer .swatch-text')


    # Espera que aparezca el precio y extrae el texto
    driver.wait_for_element("css selector", "span.price", timeout=10)
    price = driver.text("label", "span.price")

    obj = rr.find('span', class_='normal-price').find('span', class_='price-wrapper')

    return {"size": "125 ml", "price": price}

@request(max_retry=10, run_async=True, close_on_crash=True, output=None)
def scrape_primor_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('div', class_='prices').find('div', class_='normal-price').find('span', class_='price')
    price = get_price(obj)

    return price

@request(max_retry=10, run_async=True, close_on_crash=True, output=None)
def scrape_deloox_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('div', class_='main-variant-container').find('div', class_='variant-price')
    price = get_price(obj)

    return price

@request(max_retry=10, run_async=True, close_on_crash=True, output=None)
def scrape_miravia_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('div', id='pdp_countUp')
    price = get_price(obj)

    return price

@request(max_retry=10, run_async=True, close_on_crash=True, output=None)
def scrape_amazon_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('span', class_='priceToPay')
    price = get_price(obj)

    return price

def main():
    tasks = {
        'Notino - Lattafa - Asad': scrape_notino_price(data={'url': 'https://www.notino.es/lattafa/asad-eau-de-parfum-para-hombre/p-16145677/'}),
        'Brasty - Afnan - Supremacy Not Only Intense': scrape_brasty_price(data={'url': 'https://www.brasty.es/afnan-supremacy-not-only-intense-perfume-para-hombre-150-ml'}),
        'Druni - Lattafa - Asad Bourbon': scrape_druni_price(data={'url': 'https://www.druni.es/asad-bourbon-lattafa-eau-parfum-hombre'}),
        'Primor - Halloween - Halloween Man X': scrape_primor_price(data={'url': 'https://www.primor.eu/es_es/halloween-halloween-man-x-edt-112384.html?#854=66504'}),
        "Deloox - Afnan - Supremacy Collector's": scrape_deloox_price(data={'url': 'https://www.deloox.es/producto/1343240/afnan-supremacy-eau-de-parfum-edicion-de-coleccionista-100-ml.html'}),
        'Miravia - Armaf - Odyssey Mandarin Sky Elixir': scrape_miravia_price(data={'url': 'https://www.miravia.es/p/armaf-odyssey-mandarin-sky-elixir-eau-de-parfum-100ml-perume-arabe-original-para-hombre-i1373294636273528.html'}),
        'Amazon - Lattafa - Khamrah Qahwa': scrape_amazon_price(data={'url': 'https://www.amazon.es/dp/B0CWBS4NN7'})
    }

    for key, task in tasks.items():
        print(f'{key:64} {task.get()}€')

if __name__ == '__main__':
    main()
