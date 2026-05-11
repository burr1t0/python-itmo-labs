# Функция для шифрования
def encrypt(plaintext: str, shift: int):
    # Переменная для хранения шифра
    output_text = ""
    # Цикл разбивает по буквам и кодирует

    for symbol in plaintext:
        # Переменная в которой хранится код эл-та
        code_symbol = ord(symbol)
        # "ord" - выдает код эл-та

        # Если при кодировке смещение не выходит за диапазон
        if (32 <= code_symbol <= 126) and (32 <= code_symbol + shift <= 126):
            # "chr" - выдает эл-т соответствующий коду
            output_text += chr(shift + code_symbol)

        # Если при кодировке смещение выходит за диапазон и сдвиг отрицательный
        elif (32 >= code_symbol + shift) and (32 <= code_symbol <= 126):
            output_text += chr(126 - 31 + (shift + code_symbol))
            # +31 т.к. с 32-го начинаются подходящие символы

        # Если при кодировке смещение выходит за диапазон и сдвиг положительный
        elif (code_symbol + shift >= 126) and (32 <= code_symbol <= 126):
            output_text += chr((shift + code_symbol) - 126 + 31)

        else:
            # Если используются символы выходящие за диапазон [32, 126]
            output_text = "Содержит недопустимый символ"
            break

    return output_text


# Функция для дешифрования
def decrypt(ciphertext: str, shift: int):
    # Переменная для хранения шифра
    output_text = ""
    # Цикл разбивает по буквам и кодирует
    shift = -shift
    for symbol in ciphertext:
        # Переменная в которой хранится код эл-та
        code_symbol = ord(symbol)
        # "ord" - выдает код эл-та

        # Если при кодировке смещение не выходит за диапазон
        if (32 <= code_symbol <= 126) and (32 <= code_symbol + shift <= 126):
            # "chr" - выдает эл-т соответствующий коду
            output_text += chr(shift + code_symbol)

        # Если при кодировке смещение выходит за диапазон и сдвиг отрицательный
        elif (32 >= code_symbol + shift) and (32 <= code_symbol <= 126):
            output_text += chr(126 - 31 + (shift + code_symbol))
            # +31 т.к. с 32-го начинаются подходящие символы

        # Если при кодировке смещение выходит за диапазон и сдвиг положительный
        elif (code_symbol + shift >= 126) and (32 <= code_symbol <= 126):
            output_text += chr((shift + code_symbol) - 126 + 31)

        else:
            # Если используются символы выходящие за диапазон [32, 126]
            output_text = "Содержит недопустимый символ"
            break

    return output_text
