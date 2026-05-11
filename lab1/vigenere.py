# Заполнение алфавита
alf = sorted("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM")
# Заполнение ASCII алфавита
asc = ""
for i in range(32, 126 + 1):
    asc += chr(i)


# Функция для шифровки Виженера
def encrypt(plaintext: str, keyword: str):
    # Привожу ключ к нижнему регистру
    low_key = ""
    # Проверка являются ли символы буквами
    if len(keyword) == 0:
        return plaintext
    for letter in keyword:
        if (letter in alf) and (letter in asc):
            low_key += letter.lower()
        else:
            # Если встретились недопустимые символы или цифры
            continue

    # Сдвиги по алфавиту (поэтому вычитаем 1 эл-т алфавита)
    shifts = []
    for letter in low_key:
        shifts.append(ord(letter) - ord("a"))

    # Переменная для шифра
    output_text = ""
    # Переменная для сдвига по кодовому слову
    key_index = 0

    # Кодировка символов
    for symbol in plaintext:
        if 32 <= ord(symbol) <= 126:
            # Сдвиг равен элементу из "сдвига" по индексу не превышая длину ключа
            shift = shifts[key_index % len(shifts)]
            # Новый код для символа равен сумме старого кода и сдвига
            new_code = ord(symbol) + shift

            # Проверка на превышение индекса
            if new_code > 126:
                new_code = 31 + new_code - 126
            # Запись нового символа
            output_text += chr(new_code)
            # Увеличение индекса
            key_index += 1
        else:
            # При использовании символов не входящих в диапазон [32, 126]
            output_text = "Используются недопустимые символы"
            break

    return output_text


# Функция для дешифрования шифра Виженера
def decrypt(ciphertext: str, keyword: str):
    if len(keyword) == 0:

        return ciphertext

    # Привожу ключ к нижнему регистру
    low_key = ""
    # Проверка являются ли символы буквами
    for letter in keyword:
        if (letter in alf) and (letter in asc):
            low_key += letter.lower()
        else:
            # Если встретились недопустимые символы или цифры
            continue

    # Сдвиги по алфавиту (поэтому вычитаем 1 эл-т алфавита)
    shifts = []
    for letter in low_key:
        shifts.append(ord(letter) - ord("a"))

    # Переменная для де-шифра
    output_text = ""
    # Переменная для сдвига по кодовому слову
    key_index = 0

    # Цикл для декодирования букв
    for symbol in ciphertext:
        if 32 <= ord(symbol) <= 126:
            shift = shifts[key_index % len(shifts)]
            # Код изначального сим-ла равен текущему сим-лу - сдвиг
            old_code = ord(symbol) - shift

            # Проверка на выход эл-та за границы
            if old_code < 32:
                old_code = 126 - 31 + old_code
            # Добавление нового сим-ла
            output_text += chr(old_code)
            key_index += 1
        else:
            output_text = "Используются недопустимые символы"
            break

    return output_text
