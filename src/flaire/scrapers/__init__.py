import logging
import functools

from colorama import Fore, Style

from botasaurus.browser import browser, Driver
from botasaurus.request import request, Request
from botasaurus.soupify import soupify

MAX_RETRY = 3
RETRY_WAIT = 10

NOT_AVAILABLE_TEXT = {
    'NOT_AVAILABLE',
    'NO DISPONIBLE',
    'NO ESTA DISPONIBLE'
}

logger = logging.getLogger(__name__)

scrap_request = functools.partial(
    request,
    max_retry=MAX_RETRY,
    retry_wait=RETRY_WAIT,
    run_async=True,
    close_on_crash=True,
    output=None
)

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

def safe_price(func):
    @functools.wraps(func)
    def wrapper_price(*args, **kwargs):
        try:
            price = func(*args, **kwargs)
        except:
            _, data = args
            url = data['url']
            logger.warning(f"{Fore.RED}✘{Style.RESET_ALL} Something wrong with '{url}'.", exc_info=False)
            price = None
        finally:
            return price
    ###
    return wrapper_price

@scrap_request
@safe_price
def scrape_notino_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('span', {'data-testid': 'pd-price-wrapper'}) or soup.find(id='pd-price')
    price1 = get_price(obj)
    obj = soup.find('span', {'data-testid': 'pd-price'})
    price2 = get_price(obj) if obj else price1

    price = price1 if price1 < price2 else price2
    return price

@scrap_request
@safe_price
def scrape_brasty_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('dl', class_='c-pd-shopbox__row').find('dd')
    price = get_price(obj)

    return price

@scrap_request
@safe_price
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

@scrap_request
@safe_price
def scrape_primor_price(request: Request, data):
    price = None
    soup = get_soup_from_url(request, url=data['url'])

    if (obj := soup.find('div', {'x-show': '!isAvailable'})):
        obj = soup.find('div', class_='prices').find('div', class_='normal-price').find('span', class_='price')
        price = get_price(obj)

    return price

@scrap_request
@safe_price
def scrape_deloox_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('div', class_='main-variant-container').find('div', class_='variant-price')
    price = get_price(obj)

    return price

@scrap_request
@safe_price
def scrape_miravia_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('div', id='pdp_countUp')
    price = get_price(obj)

    return price

@scrap_request
@safe_price
def scrape_amazon_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('span', class_='priceToPay')
    price = get_price(obj)

    return price

@scrap_request
@safe_price
def scrape_douglas_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('div', class_='discounted-price__row')
    if obj:
        obj = obj.find_all('div')[-1]
    else:
        obj = soup.find('div', class_='product-price')

    price = get_price(obj)
    return price

@scrap_request
@safe_price
def scrape_ferwer_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('span', id='api_price')
    status = soup.find('span', class_='group-product-status-word').get_text().strip().upper()

    price = None if status in NOT_AVAILABLE_TEXT else get_price(obj)
    return price

@scrap_request
@safe_price
def scrape_perfumerias_price(request: Request, data):
    soup = get_soup_from_url(request, url=data['url'])

    obj = soup.find('div', class_='precio')
    price = get_price(obj)
    return price
