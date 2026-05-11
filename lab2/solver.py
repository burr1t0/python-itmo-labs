from minesweeper_engine import (
    generate_board,
    reveal_cell,
    toggle_flag,
    display_field,
    check_win,
    Cell,
    neighbors
)
import random
from collections import deque


class Solver:

    # добавление поля для отслеживания
    def __init__(self):
        self.opened_cells = []
        self.flagged_cells = []

    # применяет детерминированные правила для нахождения ходов
    def solve_step(self, board: list[list[Cell]]) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        rows = len(board)
        if rows > 0:
            cols = len(board[0])
        else:
            cols = 0

        # Сохранение для открытия
        save_to_open = set()
        mines_to_flag = set()
        # если нашли
        found = True

        # применяем правила, пока находим новые ходы
        while found:
            found = False

            # инициализация клетки
            for row in range(rows):
                for col in range(cols):
                    cell = board[row][col]

                    # рассматриваем открытые ячейки, у которых есть цифры
                    if not cell.is_revealed or cell.adjacent_mines == 0:
                        continue

                    # через создание временного BFS
                    neighbors_list = neighbors(row, col, rows, cols)

                    # не открытая соседняя ячейка без флага
                    unopened_neighbors = []
                    # соседняя ячейка с флагом
                    flagged_cnt = 0
                    # объявление соседних клеток
                    for n_row, n_col in neighbors_list:
                        offset_cell = board[n_row][n_col]
                        if not offset_cell.is_revealed:
                            if offset_cell.is_flagged:
                                flagged_cnt += 1
                            else:
                                unopened_neighbors.append((n_row, n_col))

                    # всего закрытых
                    total_unopened = len(unopened_neighbors) + flagged_cnt

                    # 1 правило: все закрытые - мины
                    if cell.adjacent_mines == total_unopened:
                        for n_row, n_col in unopened_neighbors:
                            if (n_row, n_col) not in mines_to_flag:
                                mines_to_flag.add((n_row, n_col))
                                found = True

                    # 2 правило: все безопасны (число равно количеству флагов)
                    if cell.adjacent_mines == flagged_cnt:
                        for n_row, n_col in unopened_neighbors:
                            if (n_row, n_col) not in save_to_open:
                                save_to_open.add((n_row, n_col))
                                found = True

        # Если базовые правила не подошли, применяем csp
        if not save_to_open and not mines_to_flag:
            csp_safe, csp_mines = self._apply_csp_rules(board)
            # Update - т.к. может добавить сразу несколько элементов
            save_to_open.update(csp_safe)
            mines_to_flag.update(csp_mines)
        return save_to_open, mines_to_flag

    # применяет csp правила с подмножествами
    def _apply_csp_rules(self, board: list[list[Cell]]):
        constraints = self._generate_constraints(board)

        if not constraints:
            return set(), set()

        # используем правило подмножеств
        new_constraints = self._apply_subset_rule(constraints)

        # новые ограничения
        safe_to_open = set()
        mines_to_flag = set()

        for variables, mine_cnt in new_constraints:
            # если нет мин рядом - все безопасны
            if mine_cnt == 0:
                safe_to_open.update(variables)
            # и наоборот если все переменные, то все мины
            elif mine_cnt == len(variables):
                mines_to_flag.update(variables)

        return safe_to_open, mines_to_flag

    # генерирует огр-я исходя из состояния текущего поля
    def _generate_constraints(self, board: list[list[Cell]]):
        rows = len(board)
        cols = len(board[0])
        constraints = []

        # поиск всех открытых, которые граничат с закрытыми
        for row in range(rows):
            for col in range(cols):
                cell = board[row][col]
                if cell.is_revealed and cell.adjacent_mines > 0:
                    neighbors_list = neighbors(row, col, rows, cols)
                    # добавляем закрытые клетки и считаем количество мин
                    variables = set()
                    known_mines = 0

                    for n_row, n_col in neighbors_list:
                        neighbors_cell = board[n_row][n_col]
                        if not neighbors_cell.is_revealed:
                            if neighbors_cell.is_flagged:
                                known_mines += 1
                            else:
                                variables.add((n_row, n_col))

                    # если нашлись переменные, то добавляем ограничения
                    if variables:
                        # оставшиеся мины
                        remaining_mines = cell.adjacent_mines - known_mines
                        if 0 <= remaining_mines <= len(variables):
                            constraints.append((frozenset(variables), remaining_mines))
        return constraints

    # применяет правило подмножеств для вывода новых ограничений
    def _apply_subset_rule(self, constraints: list):
        new_constraints = list(constraints)
        changed = True

        while changed:
            changed = False
            # текущее кол-во
            current_cnt = len(new_constraints)

            # пробегаем по всем вариантам и сравниваем их
            for i in range(current_cnt):
                for j in range(i + 1, current_cnt):
                    variants1, cnt1 = new_constraints[i]
                    variants2, cnt2 = new_constraints[j]

                    # проверка, явл-ся ли одно множество подмножеством другого
                    if variants1.issubset(variants2):
                        # variants1 - подмножество variants2
                        new_variants = variants2 - variants1
                        new_cnt = cnt2 - cnt1
                        if 0 <= new_cnt <= len(new_variants):
                            new_constraint = (frozenset(new_variants), new_cnt)
                            if new_constraint not in new_constraints:
                                new_constraints.append(new_constraint)
                                changed = True

                    elif variants2.issubset(variants1):
                        new_variants = variants1 - variants2
                        new_cnt = cnt1 - cnt2
                        if 0 <= new_cnt <= len(new_variants):
                            new_constraint = (frozenset(new_variants), new_cnt)
                            if new_constraint not in new_constraints:
                                new_constraints.append(new_constraint)
                                changed = True
        return new_constraints

    def solve_automatically(self, rows=8, cols=8, mines=10, display_progress=True):
        print("решатель работает")

        # выбираем первую ячейку
        start_row, start_col = random.randint(0, rows - 1), random.randint(0, cols - 1)

        # создание поля и открытие ячейки
        board = generate_board(rows, cols, mines, (start_row, start_col))
        reveal_cell(board, start_row, start_col, first_move=True)

        self.opened_cells.append((start_row, start_col))

        if display_progress:
            print("Первый ход: " + str(start_row) + " " + str(start_col))
            display = display_field(board, game_over=False)
            self._print_board(display)

        moves = 0
        # с небольшим запасом, т.к. решатель не всегда оптимален
        max_moves = rows * cols * 2

        while moves < max_moves:
            moves += 1

            # используем решатель
            safe_to_open, mines_to_flag = self._update_solve_step_with_probabilistic(
                board
            )

            # ставим флаги
            for row, col in mines_to_flag:
                if not board[row][col].is_flagged:
                    toggle_flag(board, row, col)
                    self.flagged_cells.append((row, col))
                    if display_progress:
                        print("Флаг: " + str(row) + " " + str(col))

            # открываем безопасные ячейки
            game_lost = False
            for row, col in safe_to_open:
                if not board[row][col].is_revealed and not board[row][col].is_flagged:
                    success = reveal_cell(board, row, col, first_move=False)
                    self.opened_cells.append((row, col))
                    if display_progress:
                        print("Открыта " + str(row) + " " + str(col))

                    if not success:
                        game_lost = True
                        break

            # если попал на мину
            if game_lost:
                if display_progress:
                    print("Поражение")
                return False, board

            if not safe_to_open and not mines_to_flag:
                random_move = self._make_random_move(board)
                if random_move:
                    row, col = random_move
                    success = reveal_cell(board, row, col, first_move=False)
                    self.opened_cells.append((row, col))
                    if display_progress:
                        print("Случайный ход: " + str(row) + " " + str(col))

                    if not success:
                        if display_progress:
                            print("Поражение")
                        return False, board
                else:
                    break

            if check_win(board):
                if display_progress:
                    print("Победа")
                return True, board

        return False, board

    # делает случайный ход в ячейку без флага
    def _make_random_move(self, board):
        # доступные
        available = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if not board[row][col].is_revealed and not board[row][col].is_flagged:
                    available.append((row, col))
        if available:
            return random.choice(available)
        else:
            return None

    # вывод поля
    def _print_board(self, grid):
        cols = len(grid[0])
        print("\n    " + " ".join(str(i) for i in range(cols)))
        print("  " + "-" * (cols * 2 + 2))
        for i, row in enumerate(grid):
            print(str(i) + " | " + " ".join(row) + " |")
        print("  " + "-" * (cols * 2 + 2))

    def display_result(self, won, board):
        # выводит итоговое поле
        display = display_field(board, game_over=True)
        self._print_board(display)

        # результаты
        if won:
            print("Победа =)")
        else:
            print("Поражение =(")

        # выводим списки
        print(f"\nВсе открытые ячейки: {sorted(self.opened_cells)}")
        print(f"Все поставленные флаги: {sorted(self.flagged_cells)}")

    # находит координаты с наименьшей вероятностью мины для безопасного хода, возвращает ее координаты
    def make_probabilistic_move(self, board: list[list[Cell]]):
        # получаем все ограничения
        constraints = self._generate_constraints(board)

        if not constraints:
            # если нет ограничений, то случайный ход
            return self._make_random_move(board)

        # поиск независимых областей
        regions = self._find_independent_regions(constraints)

        # словарь для хранения вероятностей
        probabilities = {}

        # обрабатываю каждую область отдельно
        for region_vars, region_constraints in regions:
            # находим все валидные расстановки для области
            valid_configs = self._find_valid_configurations(
                region_vars, region_constraints
            )

            if not valid_configs:
                continue

            # расчет вероятности для каждой ячейки
            for cell in region_vars:
                mine_cnt = 0
                for config in valid_configs:
                    if config.get(cell, False):
                        mine_cnt += 1
                probability = mine_cnt / len(valid_configs)
                probabilities[cell] = probability

        # Если нашли ячейки с вычисленными вероятностями
        if probabilities:
            # Находим ячейку с минимальной вероятностью мины
            min_probability = float("inf")
            best_cell = None

            for cell, prob in probabilities.items():
                if prob < min_probability:
                    min_probability = prob
                    best_cell = cell
            return best_cell
        else:
            # Если не удалось вычислить вероятности, делаем случайный ход
            return self._make_random_move(board)

    def _find_independent_regions(self, constraints: list):
        """
        Разделяет ограничения на независимые области с помощью BFS
        возвращает список кортежей: (множество_переменных_области, список_ограничений_области)
        """

        # создание графа связи между переменными
        graph = {}
        all_variables = set()

        # собираем все переменные
        for vars_set, _ in constraints:
            all_variables.update(vars_set)

        # строим граф связей
        for var in all_variables:
            graph[var] = set()

        for vars_set, _ in constraints:
            vars_list = list(vars_set)
            for i in range(len(vars_list)):
                for j in range(i + 1, len(vars_list)):
                    var1, var2 = vars_list[i], vars_list[j]
                    graph[var1].add(var2)
                    graph[var2].add(var1)

        # поиск связанных компонентов с помощью bfs
        visited = set()
        regions = []

        for var in all_variables:
            if var not in visited:
                # новая область
                regions_vars = set()
                queue = deque([var])

                while queue:
                    current_var = queue.popleft()
                    # popleft() - удаляет из начала очереди
                    if current_var not in visited:
                        visited.add(current_var)
                        regions_vars.add(current_var)
                        # добавление всех соседей
                        for neighbor in graph[current_var]:
                            if neighbor not in visited:
                                queue.append(neighbor)

                # находим ограничения для этой области
                region_constraints = []
                for vars_set, mine_cnt in constraints:
                    if vars_set.issubset(regions_vars):
                        region_constraints.append((vars_set, mine_cnt))

                regions.append((regions_vars, region_constraints))
        return regions

    def _find_valid_configurations(self, variables: set, constraints: list):
        """
        Находит все валидные расстановки мин для заданных переменных и ограничений
        перебирает все возможные конфигурации
        """
        variables_list = list(variables)
        valid_configs = []

        def is_valid(config: dict) -> bool:
            """Проверяет, удовлетворяет ли конфигурация всем ограничениям"""
            for vars_set, required_mines in constraints:
                actual_mines = sum(1 for var in vars_set if config.get(var, False))
                if actual_mines != required_mines:
                    return False
            return True

        def backtrack(current_config: dict, index: int):
            """Рекурсивный backtracking для перебора конфигураций"""
            if index == len(variables_list):
                if is_valid(current_config):
                    valid_configs.append(current_config.copy())
                return

            # Пробуем обе возможности для текущей переменной
            current_var = variables_list[index]

            # Вариант 1: без мины
            current_config[current_var] = False
            backtrack(current_config, index + 1)

            # Вариант 2: с миной
            current_config[current_var] = True
            backtrack(current_config, index + 1)

        # Запускаем backtracking
        backtrack({}, 0)
        return valid_configs

    def _update_solve_step_with_probabilistic(self, board):
        """
        Обновленный solve_step, который использует вероятностный метод когда детерминированные правила не работают
        """
        # Сначала применяем детерминированные правила
        safe_to_open, mines_to_flag = self.solve_step(board)

        # Если детерминированные правила не нашли ходов, используем вероятностный
        if not safe_to_open and not mines_to_flag:
            probabilistic_move = self.make_probabilistic_move(board)
            if probabilistic_move:
                print(f"вероятностный решатель выбрал {probabilistic_move}")
            if probabilistic_move:
                safe_to_open.add(probabilistic_move)

        return safe_to_open, mines_to_flag


def main():
    solver = Solver()

    # Автоматическое решение игры
    won, final_board = solver.solve_automatically(
        rows=8, cols=8, mines=10, display_progress=True
    )

    # показываем результат
    solver.display_result(won, final_board)


if __name__ == "__main__":
    main()
