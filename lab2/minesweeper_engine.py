from random import sample
from dataclasses import dataclass
from _collections import deque


@dataclass
class Cell:
    # Объявление ячейки
    # наличие мины
    is_mine: bool = False
    # открыта?
    is_revealed: bool = False
    # есть ли флаг
    is_flagged: bool = False
    # мин рядом:
    adjacent_mines: int = 0


# функция для получения координат соседей
def neighbors(row: int, col: int, rows: int, cols: int) -> list[tuple[int, int]]:
    neighbors_list = []
    for row_offset in [-1, 0, 1]:
        for col_offset in [-1, 0, 1]:
            if row_offset == 0 and col_offset == 0:
                continue  # пропускаем саму ячейку
            possible_row, possible_col = row + row_offset, col + col_offset
            if 0 <= possible_row < rows and 0 <= possible_col < cols:
                neighbors_list.append((possible_row, possible_col))
    return neighbors_list


# # создание поля
# def generate_board(rows: int, cols: int, num_mines: int, safe_coords: tuple[int, int]) -> list[list[Cell]]:
#     # Создаем полностью пустое поле
#     field = []
#     for i in range(rows):
#         row = []
#         for j in range(cols):
#             row.append(Cell())
#         field.append(row)
#
#     # Сразу размещаем мины
#     field = place_mines(field, num_mines, safe_coords)
#     return field
#
#
# # размещение мин на существующем поле
# def place_mines(field: list[list[Cell]], num_mines: int, safe_coords: tuple[int, int]) -> list[list[Cell]]:
#     rows, cols = len(field), len(field[0])
#     safe_row, safe_col = safe_coords
#
#     # безопасная зона - только сама ячейка первого хода
#     safe_zone = set()
#     safe_zone.add((safe_row, safe_col))
#
#     # создание возможных позиций для мин (исключая безопасную зону)
#     mine_positions = []
#     for row in range(rows):
#         for col in range(cols):
#             if (row, col) not in safe_zone:
#                 mine_positions.append((row, col))
#
#     # Проверяем, что достаточно места для мин
#     available_positions = len(mine_positions)
#     actual_mines = min(num_mines, available_positions)
#
#     # размещение мин (случайный выбор без повторений)
#     for row, col in sample(mine_positions, actual_mines):
#         field[row][col].is_mine = True
#
#     # подсчет соседних мин для всех ячеек
#     for row in range(rows):
#         for col in range(cols):
#             if not field[row][col].is_mine:
#                 mine_count = 0
#                 for row_offset, col_offset in neighbors(row, col, rows, cols):
#                     if field[row_offset][col_offset].is_mine:
#                         mine_count += 1
#                 field[row][col].adjacent_mines = mine_count
#     return field

def generate_board(rows: int, cols: int, num_mines: int, safe_coords: tuple[int, int]) -> list[list[Cell]]:
    # Создаем полностью пустое поле
    field = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row.append(Cell())
        field.append(row)

    safe_row, safe_col = safe_coords

    # безопасная зона - только сама ячейка первого хода
    safe_zone = set()
    safe_zone.add((safe_row, safe_col))

    # создание возможных позиций для мин (исключая безопасную зону)
    mine_positions = []
    for row in range(rows):
        for col in range(cols):
            if (row, col) not in safe_zone:
                mine_positions.append((row, col))

    # Проверяем, что достаточно места для мин
    available_positions = len(mine_positions)
    actual_mines = min(num_mines, available_positions)

    # размещение мин (случайный выбор без повторений)
    for row, col in sample(mine_positions, actual_mines):
        field[row][col].is_mine = True

    # подсчет соседних мин для всех ячеек
    for row in range(rows):
        for col in range(cols):
            if not field[row][col].is_mine:
                mine_count = 0
                # используем функцию neighbors для обхода соседей
                for nr, nc in neighbors(row, col, rows, cols):
                    if field[nr][nc].is_mine:
                        mine_count += 1
                field[row][col].adjacent_mines = mine_count

    return field

def reveal_cell(
    field: list[list[Cell]], start_row: int, start_col: int, first_move: bool = False
) -> bool:
    rows, cols = len(field), len(field[0])

    # проверка границ (если координаты вне поля, то это некорректный ввод, игра продолжится)
    if not (0 <= start_row < rows and 0 <= start_col < cols):
        return True

    # объявление ячейки
    cell = field[start_row][start_col]

    # проверка пропуска
    if cell.is_revealed or cell.is_flagged:
        return True

    # проверка мины, если не первый ход
    if not first_move and cell.is_mine:
        cell.is_revealed = True
        return False

    # использование очереди для всех
    queue = deque()
    queue.append((start_row, start_col))

    while queue:
        # queue.popleft() - извлекает и удаляет элемент из очереди
        row, col = queue.popleft()
        # ячейка с которой работаю в данный момент
        current_cell = field[row][col]

        # пропуск если открыта или флаг
        if current_cell.is_revealed or current_cell.is_flagged:
            continue

        # если не вышел из цикла, то открываю ячейку
        current_cell.is_revealed = True

        # если рядом нет мин, добавляю соседние в очередь
        if current_cell.adjacent_mines == 0:
            for row_offset, col_offset in neighbors(row, col, rows, cols):
                offset_cell = field[row_offset][col_offset]
                if (
                        not offset_cell.is_revealed
                        and not offset_cell.is_flagged
                        and not offset_cell.is_mine
                ):
                    queue.append((row_offset, col_offset))
    return True


# поставить или убрать флаг
def toggle_flag(field: list[list[Cell]], row: int, col: int) -> bool:
    if 0 <= row < len(field) and 0 <= col < len(field[0]):
        cell = field[row][col]
        if not cell.is_revealed:
            # если ячейка закрыта, то поменяет значение флага на противоположный
            cell.is_flagged = not cell.is_flagged
            return True
    return False


# проверка победы
def check_win(field: list[list[Cell]]) -> bool:
    for row in field:
        for cell in row:
            # логика: если не осталось закрытой ячейки, которая не является миной, то победа
            if not cell.is_mine and not cell.is_revealed:
                return False
    return True


# отображение поля с символами
def display_field(field: list[list[Cell]], game_over: bool = False) -> list[list[str]]:
    display = []
    for row in field:
        display_row = []
        for cell in row:
            if cell.is_flagged:
                display_row.append("F")
            elif not cell.is_revealed and not game_over:
                display_row.append("#")
            elif cell.is_mine and game_over:
                display_row.append("*")
            elif cell.is_revealed:
                if cell.adjacent_mines > 0:
                    display_row.append(str(cell.adjacent_mines))
                else:
                    display_row.append("0")
            else:
                display_row.append("#")
        display.append(display_row)
    return display
