import requests
from bs4 import BeautifulSoup as bs
import lxml
import csv
import telebot
import io

def get_html(url):
    response = requests.get(url)
    return response.text

def get_data(html):
    soup = bs(html, "lxml")
    catalog = soup.find("div", class_ = "list-view")
    products = catalog.find_all('div', class_="item product_listbox oh")
    for product in products:
        try:
            product_title = product.find('strong').find("a").text
        except:
            product_title = ""
        try:
            product_image = product.find('div',class_ = "listbox_img pull-left" ).find('img').get('src')
            product_image = f"https://www.kivano.kg{product_image}"
        except:
            product_image = ""
        try:
            product_price_new = product.find('div', class_ = 'motive_box pull-right').find('strong').text
        except:
            product_price_new = ""
        # try:
        #     product_price_old = product.find('div', class_ = "motive_box pull-right").find('div', class_ = "listbox_price text-center").find("div", class_ = "color7").find('span', class_ = "oldprice").text
        #     product_discount = product.find('div', class_ = "motive_box pull-right").find('div', class_ = "listbox_price text-center").find("div", class_ = "color7").find('span', class_ = "econ_rate").text
        # except:
        #     product_price_old = ""
        #     product_discount = ""

        data = {
            "product_title": product_title,
            "product_price_new": product_price_new,
            "product_image": product_image,
            # "product_price_old": product_price_old,
            # "product_discount": product_discount,
            
        }
       
        write_csv(data)

def write_csv(data):
    with open('products_kivano.csv', 'a') as csv_file:
        names = ["product_title","product_price_new","product_image",] # "product_price_old","product_discount"
        writer = csv.DictWriter(csv_file, delimiter = "|", fieldnames = names)
        writer.writerow(data)        

def get_last_page(html):
    """
    эта функция находит ссылку на последнюю страницу
    """
    soup = bs(html, 'lxml')
    url_last_page = soup.find('li', class_ = "last").find("a").text
    return int(url_last_page)



def main():
    url = "https://www.kivano.kg/mobilnye-telefony"
    html = get_html(url)
    last_page = get_last_page(html)
    get_data(html)
    for page in range(1, last_page+1):
        url = f"{url}?page={page}"
        html = get_html(url)
        data = get_data(html)

main()


    
