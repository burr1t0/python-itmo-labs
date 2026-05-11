import asyncio
import aiohttp  # type: ignore[import-not-found]
from bs4 import BeautifulSoup  # type: ignore[import-not-found]
import os
import sys
from dotenv import load_dotenv  # type: ignore[import-not-found]
from typing import Optional, Any
import constants
# загрузка переменных из енв
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

if not TOKEN:
    print('токен не найден')
    sys.exit(1)
if not OPENWEATHER_API_KEY:
    print('api не найден')
    sys.exit(1)

# глоб-й словарь для хранения состояний пользователей
_user_states: dict[int, str] = {}


async def send_message(chat_id: int, text: str,
                       show_keyboard: bool = False) -> None:
    """отправка сообщений кнопками
    args:
        chat_id - id чата для отправки сообщений
        text - текст соо-я
        show_keyboard - показ клавиатуры

    returns:
        None
    """
    url = f'{BASE_URL}/sendMessage'

    payload = {'chat_id': chat_id, 'text': text}

    # добавление клавиатуры
    if show_keyboard:
        keyboard = {
            'keyboard': [['/quote', '/headlines'], ['/weather', '/help']],
            'resize_keyboard': True,  'one_time_keyboard': False}
        payload['reply_markup'] = keyboard

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            await response.json()


async def get_updates(offset: Optional[int] = None) -> list[dict[str, Any]]:
    """получение новых сообщений
    args:
        offset - идентификатор 1-го обновления для получ-я
    returns:
        список обновл-й от тг API
    """
    url = f'{BASE_URL}/getUpdates'
    params = {'timeout': 30, 'offset': offset}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data: dict[str, Any] = await response.json()
            result: list[dict[str, Any]] = data.get('result', [])
            return result


# асинхронные функции скрапинга
async def get_quote() -> str:
    """получение цитаты
    returns:
        строка с цитатой
    """
    try:
        url = constants.QUOTE_API_URL
        params = {'method': 'getQuote', 'format': 'json', 'lang': 'ru'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                quote = data.get('quoteText', 'Нет цитаты')
                author = data.get('quoteAuthor', 'Автор неизвестен')
                return f'Цитата дня:\n"{quote}"\n— {author}'
    except asyncio.TimeoutError:
        print("таймаут запроса цитаты")
        return 'Цитата дня:\n"таймаут."\n— Бот'
    except aiohttp.ClientConnectionError:
        print("ошибка подключения к API цитат")
        return 'Цитата дня:\n"нет сети."\n— Бот'
    except aiohttp.ClientResponseError:
        print("http ошибка от API цитат")
        return 'Цитата дня:\n"ошибка сервера."\n— Бот'
    except Exception:
        return 'Цитата дня:\n"Сегодня цитаты нет."\n— Бот'


# скраперы для новостей
async def scrape_news_site1() -> str:
    """парсинг новостей с РИА
    returns:
        строка с новостями или соо-е об ошибке
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(constants.NEWS_URL_RIA) as response:
            html = await response.text()

            def parse_html() -> list[str]:
                soup = BeautifulSoup(html, 'html.parser')
                # поиск заголовка
                titles = soup.find_all('a', class_='cell-list__item-link')
                news = []
                for t in titles[:3]:
                    text = t.get_text(strip=True)
                    if text:
                        news.append(f"- {text}")
                return news

            news = await asyncio.to_thread(parse_html)

            if news:
                return "РИА Новости:\n" + "\n".join(news)
            return "РИА: новостей нет"


async def scrape_news_site2() -> str:
    """новости с Коммерсанта
    returns:
        строка с новостями или соо-е об ошибке
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(constants.NEWS_URL_KOMMERSANT) as response:
            html = await response.text()

            def parse_html() -> list[str]:
                soup = BeautifulSoup(html, 'html.parser')
                # поиск заголовков
                titles = soup.find_all('a', class_='uho__link')
                news = []
                for t in titles[:3]:
                    text = t.get_text(strip=True)
                    if text:
                        news.append(f"- {text}")
                return news

            news = await asyncio.to_thread(parse_html)

            if news:
                return "Коммерсантъ:\n" + "\n".join(news)
            return "Коммерсантъ: новостей нет"


async def get_headlines() -> str:
    """получение всех новостей"""

    ria_news = scrape_news_site1()
    kommersant_news = scrape_news_site2()

    # запуск двух скраперов одновременно
    ria, kom = await asyncio.gather(ria_news, kommersant_news)

    # сборка ответов
    return f"{ria}\n\n{kom}"


# ф-ции для работы с погодой
async def get_weather(city: str) -> str:
    """получение погоды
    args:
        city - назв-е города
    returns:
        строка с инф-ей о погоде или ошибка
    """
    url = constants.WEATHER_API_URL
    params = {'q': city, 'appid': OPENWEATHER_API_KEY,
              'units': 'metric', 'lang': 'ru'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                return f"Погода в {city}:\n{temp}°C, {desc}"
            else:
                return f"не нашел {city}"


# осн-й цикл обработки сообщений
async def handle_updates() -> None:
    """главный цикл бота"""
    offset = 0

    while True:
        updates = await get_updates(offset)

        for update in updates:
            offset = update['update_id'] + 1

            if 'message' not in update:
                continue

            message = update['message']
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            text = message.get('text', '').strip()

            # проверка состояния FSM
            if user_id in _user_states:
                # пользователь ввёл город для погоды
                weather = await get_weather(text)
                await send_message(chat_id, weather)
                del _user_states[user_id]
                continue

            # обработка команд
            if text == '/start' or text == '/help':
                reply = ("Доступные команды:\n"
                         "/quote - цитата дня\n"
                         "/headlines - новости (РИА + Коммерсант)\n"
                         "/weather - погода в любом городе\n"
                         "/help - эта справка")
                # отправка команд с клав-ры
                await send_message(chat_id, reply, show_keyboard=True)

            elif text == '/quote':
                quote = await get_quote()
                await send_message(chat_id, quote)

            elif text == '/headlines':
                await send_message(chat_id, "поиск новостей")
                news = await get_headlines()
                await send_message(chat_id, news)

            elif text == '/weather':
                _user_states[user_id] = 'waiting_for_city'
                await send_message(chat_id, "введите город:")

            elif text:  # Любое другое сообщение
                await send_message(chat_id,
                                   f"Вы написали: {text}\n\nИсп. /help")

        await asyncio.sleep(1)


# главная функция
async def main() -> None:
    print("запуск бота")
    await handle_updates()


if __name__ == '__main__':
    asyncio.run(main())
