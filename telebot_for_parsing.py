import requests
from bs4 import BeautifulSoup as bs
import telebot
from telebot import types
import io
import csv

bot = telebot.TeleBot("Your Token here")

keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
button_parse = types.KeyboardButton("/parse")
button_start = types.KeyboardButton("/start")
keyboard.add(button_parse, button_start)

def get_html(url):
    response = requests.get(url)
    return response.text

def get_data(html, csv_file):
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
        try:
            product_price_old = product.find('div', class_ = "motive_box pull-right").find('div', class_ = "listbox_price text-center").find("div", class_ = "color7").find('span', class_ = "oldprice").text
            product_discount = product.find('div', class_ = "motive_box pull-right").find('div', class_ = 'listbox_price text-center').find('div', class_ = 'color7').find('span', class_ = 'econ_rate').text
        except:
            product_price_old = ""
            product_discount = ""

        data = {
            "product_title": product_title,
            "product_image": product_image,
            "product_price_old": product_price_old,
            "product_discount": product_discount,
            "product_price_new": product_price_new
        }
       
        write_csv(data, csv_file)

def write_csv(data, csv_file):
    writer = csv.DictWriter(csv_file, delimiter="|", fieldnames=["product_title", "product_image", "product_price_old", "product_discount", "product_price_new"])
    writer.writerow(data)  

def get_last_page(html):
    """
    Функция проверяет и находит последнюю страницу, если страница одна то возвращает пустую строку.
    """
    soup = bs(html, 'lxml')
    try:
        url_last_page = soup.find('li', class_ = "last").find("a").text
        return int(url_last_page)
    except:
        return ""

@bot.message_handler(commands = ['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Здравствуйте,! Вы можете воспользоватся командой /parse для получения данных с сайта Kivano", reply_markup=keyboard)

@bot.message_handler(commands=['parse'])
def handle_parse(message):
    bot.send_message(message.chat.id, "Введите URL категории сайта Kivano.kg для парсинга(пример : https://www.kivano.kg/mobilnye-telefony):")
    bot.register_next_step_handler(message, process_url_step)

@bot.message_handler(func=lambda message: True)
def process_url_step(message):
    url = message.text
    if is_valid_url(url) != False:
        csv_file = main(url)
        if csv_file:
            csv_file.seek(0)
            with io.BytesIO(csv_file.getvalue().encode()) as output:
                output.name = 'parsed_data.csv'
                bot.send_document(message.chat.id, output)
                bot.send_message(message.chat.id, "Для просмотра файла можно воспользоватся сайтом https://www.convertcsv.com/csv-viewer-editor.htm")
                bot.send_message(message.chat.id, "Если вам нужно получить информацию по другому разделу, нажмите на кнопку parse или введите команду /parse")
        else:
            bot.send_message(message.chat.id, "Не удалось получить данные с сайта")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректный URL, начинающийся с 'https://www.kivano.kg/'.")

def is_valid_url(url):
    if url.startswith("https://www.kivano.kg/") and url != "https://www.kivano.kg/":
        return url
    else:
        return False

def main(url):
    html = get_html(url)
    print(f"Это в main {url}")
    last_page = get_last_page(html)
    csv_file = io.StringIO()
    csv_file.write("product_title|product_image|product_price_old|product_discount|product_price_new\n")
    if last_page == '':
        get_data(html, csv_file)
    else:
        for page in range(1, last_page+1):
            url = f"{url}?page={page}"
            html = get_html(url)
            get_data(html, csv_file)
            print(f"{page} из {last_page} обработано!")
            
        
    return csv_file

bot.polling()

