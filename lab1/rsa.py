# Проверка числа на простоту
def is_prime(n: int):
    # Т.к. не простые числа
    if n == 1 or n == 0:

        return False

    # Если у числа есть делитель, то оно не простое
    for d in range(2, int(n**0.5) + 1):
        if n % d == 0:

            return False

    # Если не нашлось дел-ля, то оно простое
    return True


# Нахождение наибольшего общего делителя
def gcd(a: int, b: int):
    # Поиск с помощью алг. Евклида
    while b != 0:
        a, b = b, (a % b)

    return a


# Нахождение числа "d", которое (e * d) % phi = 1
def multiplicative_inverse(e: int, phi: int):
    # Если у чисел есть общий делитель (кроме 1), то они будут не взаимно простые
    if gcd(e, phi) != 1:

        return print("e, phi не взаимно простые числа")

    # Поиск "d" перебором
    d = 1
    while d < phi:
        if (d * e) % phi == 1:

            return d
        d += 1

    return print("Нет такого эл-та(")


# Генерация открытого и закрытого ключа
def generate_keypair(p: int, q: int):
    # Проверка, что числа простые
    if not (is_prime(p) and is_prime(q)):

        return print("Числа должны быть простыми")

    # Вычисление модуля "n" для обоих ключей
    n = p * q
    # Функция, значение которой равно количеству натуральных чисел, меньших или равных n, и взаимно простых с ним
    phi = (p - 1) * (q - 1)
    # Поиск экспоненты взаимно простой с "phi"
    e = 2
    while gcd(e, phi) != 1:
        e += 1
    # Вычисление закрытой экспоненты
    d = multiplicative_inverse(e, phi)

    return (e, n), (d, n)


# Функция для шифрования
def encrypt(public_key: tuple[int, int], text: str):
    # Объявление открытого ключа
    e, n = public_key
    # Переменная для зашифрованного слова
    output_text = []

    # Цикл для шифрования каждого символа
    for symbol in text:
        old_code = ord(symbol)

        # Возведение кода старого символа в степень с учетом модуля
        new_code_symbol = pow(old_code, e, n)
        # Добавление кода нового символа
        output_text.append(new_code_symbol)

    return output_text


# Функция для дешифрования
def decrypt(private_key: tuple[int, int], cipher: list[int]):
    # Объявление закрытого ключа
    d, n = private_key
    # Переменная для декодированного текста
    output_text = ""

    # Цикл для дешифрования каждого символа
    for code_symbol in cipher:
        # Возведение кода символа в степень по модулюБ для получения кода изначального символа
        m = pow(code_symbol, d, n)
        # Добавление дешифрованного символа
        output_text += chr(m)

    return output_text
