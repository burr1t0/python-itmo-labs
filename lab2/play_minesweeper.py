from minesweeper_engine import (
    generate_board,
    reveal_cell,
    toggle_flag,
    display_field,
    check_win
)


# изображение поля
def print_board(grid):
    cols = len(grid[0])
    # получили кол-во столбцов и нумеруем их
    print("\n    " + " ".join(str(i) for i in range(cols)))
    # отделение поля (получено методом тыка..)
    print("  " + "-" * (cols * 2 + 2))
    # вывод строк с номерами
    for i, row in enumerate(grid):
        # тоже подбором
        print(str(i) + " | " + " ".join(row) + " |")
    # нижняя черта таблицы
    print("  " + "-" * (cols * 2 + 2))


# получение команд и аргументов
def get_command():
    while True:
        user_input = (
            input("введите команду, затем строку, затем столбец: ").strip().split()
        )

        # если пусто
        if not user_input:
            continue

        # отдельно команда приведенная к нижнему регистру
        command = user_input[0].lower()

        if command in ["quit", "exit", "q"]:
            return "quit", 0, 0

        if command in ["open", "o", "flag", "f"]:
            if len(user_input) != 3:
                print("Недостаточно аргументов или слишком много аргументов")
                continue
            # проверка, явл-ся ли строка и столбец целыми числами
            elif user_input[1].isdigit() and user_input[2].isdigit():
                row, col = int(user_input[1]), int(user_input[2])
                return command, row, col
            else:
                print("строка и столбец должны быть целыми")
        else:
            print("Используйте команду в виде (команда, строка, столбец)")


def main():
    print("Игра сапер")
    print("Возможные команды:")
    print("open или o; flag или f; quit или q или exit")

    # Получение параметров поля от пользователя
    while True:
        rows_input = input("Введите количество строк: ")
        cols_input = input("Введите количество столбцов: ")
        mines_input = input("Введите количество мин: ")

        if not (rows_input.isdigit() and cols_input.isdigit() and mines_input.isdigit()):
            print("Пожалуйста, введите целые положительные числа")
            continue

        rows_ = int(rows_input)
        cols_ = int(cols_input)
        mines_ = int(mines_input)

        if rows_ <= 0 or cols_ <= 0 or mines_ <= 0:
            print("Все значения должны быть положительными числами")
            continue

        if mines_ >= rows_ * cols_:
            print("Количество мин не может быть больше или равно общему количеству ячеек")
            continue
        break

    first_move = True
    board = None
    game_lost = False

    while True:
        command, row, col = get_command()

        if command == "quit":
            print("Выход из игры")
            break

        # Первый ход
        if first_move:
            # создание пустого поля
            board = generate_board(rows_, cols_, mines_, (row, col))
            # Открытие 1-й ячейки
            success = reveal_cell(board, row, col, first_move=True)
            first_move = False
        else:
            if command in ["open", "o"]:
                success = reveal_cell(board, row, col, first_move=False)
                if not success:
                    # если открыли мину
                    game_lost = True
                    display = display_field(board, game_over=True)
                    print_board(display)
                    break

            elif command in ["flag", "f"]:
                toggle_flag(board, row, col)

        display = display_field(board, game_over=False)
        print_board(display)

        if check_win(board):
            print("Победа!")
            break

    if game_lost:
        print("Поражение =(")
    else:
        print("Пока!")


# если файл запущен, то выполнится ф-я main
if __name__ == "__main__":
    main()
