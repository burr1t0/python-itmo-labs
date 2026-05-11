import requests  # type: ignore[import-untyped]
import time
import os
from dotenv import load_dotenv  # type: ignore[import-not-found]
from typing import Optional, Any
import constants

# загрузка переменных из енв
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'


def send_message(chat_id: int, text: str) -> None:
    """отправка сообщения
    args:
        chat_id - id чата для соо-я
        text - текст соо-я
    returns:
        None
    """
    url = f'{BASE_URL}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}

    try:
        requests.post(url, json=payload, timeout=5)
    except requests.exceptions.Timeout:
        print("таймаут отправки соо-я")
    except requests.exceptions.ConnectionError:
        print("ошибка подключения к тг апи")
    except requests.exceptions.HTTPError:
        print("http ошибка от тг")
    except Exception:
        print("неизв-я ошибка")


def get_updates(offset: Optional[int] = None) -> list[dict[str, Any]]:
    """получение новых сообщений
    args:
        offset - идентификатор 1-го обновления для получ-я
    returns:
        список обновлений от тг API
    """
    url = f'{BASE_URL}/getUpdates'
    params = {'timeout': 30, 'offset': offset}

    try:
        response = requests.get(url, params=params, timeout=35)
        data: dict[str, Any] = response.json()
        result: list[dict[str, Any]] = data.get('result', [])
        return result
    except requests.exceptions.Timeout:
        print("таймаут отправки соо-й")
        return []
    except requests.exceptions.ConnectionError:
        print("ошибка подкл-я к тг апи")
        return []
    except requests.exceptions.HTTPError:
        print("http ошибка от тг")
        return []
    except Exception:
        return []


def get_quote() -> str:
    """синхронное получение цитаты
    returns:
        строка с цитатой
    """
    try:
        url = constants.QUOTE_API_URL
        params = {'method': 'getQuote', 'format': 'json', 'lang': 'ru'}

        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        quote = data.get('quoteText', 'Нет цитаты')
        author = data.get('quoteAuthor', 'Автор неизвестен')
        return f'Цитата дня:\n"{quote}"\n— {author}'
    except requests.exceptions.Timeout:
        print("таймаут запроса цитат")
        return 'Цитата дня:\n"таймаут."\n— Бот'
    except requests.exceptions.ConnectionError:
        print("ошибка опдкл-я к апи цитат")
        return 'Цитата дня:\n"нет сети."\n— Бот'
    except requests.exceptions.HTTPError:
        print("http ошибка от апи цитат")
        return 'Цитата дня:\n"ошибка сервера."\n— Бот'
    except Exception:
        return 'Цитата дня:\n"Сегодня цитаты нет."\n— Бот'


def main() -> None:
    """главный цикл бота"""
    print("бот запущен")
    offset = 0

    try:
        while True:
            # получ-е сообщений
            updates = get_updates(offset)

            for update in updates:
                offset = update['update_id'] + 1

                if 'message' not in update:
                    continue

                message = update['message']
                chat_id = message['chat']['id']
                text = message.get('text', '').strip()

                # обработка команд
                if not text:
                    continue

                if text == '/start' or text == '/help':
                    reply = ("Привет!\n"
                             "Команды:\n"
                             "/quote - цитата\n"
                             "Любой текст - эхо")
                    send_message(chat_id, reply)

                elif text == '/quote':
                    quote = get_quote()
                    send_message(chat_id, quote)

                else:
                    send_message(chat_id, f"Вы: {text}")

            # пауза между проверками
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nБот остановлен")


if __name__ == '__main__':
    main()
