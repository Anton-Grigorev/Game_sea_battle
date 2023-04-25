# Game - "Sea Battle" / Игра - "Морской Бой"
from random import randint                  # Для определения координат

# Создание классов внутренней логики программы:

# Создание классов возможных Исключений
class BoardException(Exception):            # Создание родительского класса
    ...

class OutBoardException(BoardException):
    def __str__(self):
        return 'Выстрел вне доски'

class RepeatExpection(BoardException):
    def __str__(self):
        return 'Повторное попадание'

class BoardWrongShipException(BoardException):
    ...


# Создание класса точек на поле
class Dot:
    # Инициализация атрибутов
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Переопределения магического метода сравнения
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # Переопределение магического метода вывода информации
    def __repr__(self):
        return f'({self.x}, {self.y})'


# Создание класса для корабля на поле
class Ship:
    # Инициализация атрибутов
    def __init__(self, bow, l, direction):
        self.bow = bow                      # Точка, где расположен нос корабля
        self.len = l                        # Длина корабля
        self.direction = direction          # Направление корабля (верт/гориз)
        self.lives = l                      # Количество жизней (сколько точек еще не подбито)

    # Создание метода для получения списка всех точек корабля
    # Метод через декоратор превращаем в свойство для удобства в последющем
    @property
    def dots(self):
        ship_dots = []                      # Создаем список, который будет возвращен

        # Запуск цикла для формирования корабля
        for i in range(self.len):
            cur_x = self.bow.x              # Координата носа корабля для определения вектора увеличения
            cur_y = self.bow.y              # Координата носа корабля для определения вектора увеличения

            if self.direction == 0:         # Если направление == 0, увеличиваем координату "х"
                cur_x += i

            elif self.direction == 1:       # Если направление == 1, увеличиваем координату "y"
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))     # Формирование списка точек корабля

        return ship_dots                    # Возвращение заполненного списка точек координат корабля

    # Создание метода определения попадания в корабль
    def shooten(self, shot):
        return shot in self.dots            # Возвращает True, если есть совпадение координат (попадание)


# Создание класса игровой доски
class Board:
    # Иницилизация атрибутов
    def __init__(self, hid=False, size=6):
        self.hid = hid                      # Параметр видимости доски
        self.size = size                    # Парарметр размера доски
        self.count = 0                      # Счетчик для определения количества пораженных кораблей

        self.field = [[' '] * size for _ in range(size)]      # Создание игрового поля

        self.busy = []                      # Создание списка занятых координат
        self.ships = []                     # Создание списка координат кораблей


    # Создание игровой доски - отрисовка через переопределение магического метода
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"        # Верхнее поле
        for i, row in enumerate(self.field):        # Отрисовка самого поля с числовым обозначение первого столбца
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("#", " ")
        return res

    # Создание метода проверки выхода за игровую доску
    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # Создание метода для корректного заполнения поля кораблями
    def contour(self, ship, verb=False):
        near = [                                    # Определение списка всех сдвигов от заданной точки
            (-1, -1), (-1, 0), (-1, 1),             # для правильной расстановки кораблей по полю
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."      # Запоминание и отметка точки выстрела
                    self.busy.append(cur)                   # Добавление в список "занятых"



    # Создание метода добавления кораблей на игровую доску
    def add_ship(self, ship):

        # Проверка на выход за границу поля и на занятость
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        # Отрисовка корабля на поле и добавление в список занятых полей
        for d in ship.dots:
            self.field[d.x][d.y] = "#"
            self.busy.append(d)

        self.ships.append(ship)                             # Добавляем список собственных кораблей
        self.contour(ship)                                  # Обводим их по контуру

    # Создание метода проверки и фиксации выстрелов
    def shot(self, d):
        if self.out(d):                                     # Проверка на выстрел вне игрового поля
            raise OutBoardException()

        if d in self.busy:                                  # Проверка на выстрел в занятое место
            raise RepeatExpection()

        self.busy.append(d)                                 # Добавляем в список занятых данный выстрел

        for ship in self.ships:
            if ship.shooten(d):                             # Проверка на попадание по кораблю
                ship.lives -= 1
                self.field[d.x][d.y] = "X"                  # В место попадания ставим "Х"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)           # Включение контура корабля
                    print("Корабль уничтожен!")
                    return False                            # Чтобы передать ход другому игроку
                else:
                    print("Корабль ранен!")
                    return True                             # Чтобы выстрелить еще раз

        # Фиксируем попадание в молоко точкой
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    # Обнуляем список занятых точек перед началом игры
    def begin(self):
        self.busy = []

# Создание классов внешенй логики программы

class Player:                                               # Создание родительского класса для игроков
    # Инициализация атрибутов (свей доски и доски соперника)
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    # Создание метода-запроса на координаты выстрела. Будет реализовываться в поклассах
    def ask(self):
        raise NotImplementedError()

    # Создаем метод бесконечного хода в игре
    def move(self):
        while True:
            try:
                target = self.ask()                         # Запрос участника на координаты выстрела
                repeat = self.enemy.shot(target)            # Производится выстрел
                return repeat
            except BoardException as e:
                print(e)

# Создаем дочерний класс игрока - компьютера
class Comp(Player):

    # Полиморфизм метода ask
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))               # Случайным образом выбираем координаты
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")       # Показываем что выбрал компьютер
        return d


# Создаем дочерний класс игрока - компьютера
class User(Player):

    # Полиморфизм метода ask
    def ask(self):
        while True:
            cords = input("Ход игрока: ").split()

            if len(cords) != 2:                              # Проверка на наличие только 2-х символов
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):        # Проверка на наличие только 2-х цифр
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)                            # Присвоение верных координат, тк отсчет не от 0


# Создаем главный класс игры
class Game:
    # Иницилизация атрибутов
    def __init__(self, size=6):
        self.size = size
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.comp = Comp(co, pl)
        self.user = User(pl, co)

    # Создание метода возврата подготовленной доски
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    # Создаем метоод для установки кораблей на доску случайным образом
    def random_place(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    # Создание метода приветствия
    def greet(self):
        print("-------------------")
        print("  Welcome to game  ")
        print("   'Sea Battle'    ")
        print("-------------------")
        print(" Вводим 2 значения:")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
        print()
        print()


    # Создаем метод показа доски
    def show_board(self):
        print("-" * 27)
        print("    Доска пользователя:")
        print(self.user.board)
        print("-" * 27)
        print("    Доска компьютера:")
        print(self.comp.board)

    # Создаем метод для хода игрока
    def loop(self):
        num = 0                                     # Для определения чей ход
        while True:
            self.show_board()
            if num % 2 == 0:
                print("-" * 27)
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("-" * 27)
                print("Ходит компьютер!")
                repeat = self.comp.move()

            if repeat:
                num -= 1

            if self.comp.board.count == len(self.comp.board.ships):
                print()
                print("-" * 27)
                print("Пользователь выиграл!")
                break

            if self.user.board.count == len(self.user.board.ships):
                print()
                print("-" * 27)
                print("Компьютер выиграл!")
                break
            num += 1

    # Создаем метод начала игры
    def start(self):
        self.greet()
        self.loop()


if __name__ == '__main__':
    my_game = Game()
    my_game.start()