from random import choice, randint

import pygame

from config import (
    WALL_KICK_DATA,
    TETROMINOS, 
    TETROMINOS_COLORS,
)


class Tetromino:
    def __init__(self, board):
        self.board = board
        self.block_size = board.block_size
        self.shape_name = choice(list(TETROMINOS.keys()))
        self.rotation = randint(0, 3)
        self.x = 0
        self.y = -1
    
    def is_valid_position(self, dx=0, dy=0, rotation=None):
        """Проверяет валидность позиции фигуры"""
        temp_rotation = rotation if rotation is not None else self.rotation
        shape = TETROMINOS[self.shape_name][temp_rotation]
        
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = self.x + col_idx + dx
                    new_y = self.y + row_idx + dy
                    
                    # Проверка границ
                    if new_x < 0 or new_x >= self.board.width or new_y >= self.board.height:
                        return False
                    # Проверка столкновений с другими блоками (если y >= 0)
                    if new_y >= 0 and self.board.grid[new_y][new_x]:
                        return False
        return True

    @property
    def shape(self):
        return TETROMINOS[self.shape_name][self.rotation]
    
    @property
    def color(self):
        return TETROMINOS_COLORS[self.shape_name]

    def rotate(self, direction=1):
        if self.shape_name == "O":  # Квадрат не вращается
            return True

        old_rotation = self.rotation
        old_x, old_y = self.x, self.y

        self.rotation = (self.rotation + direction) % 4
        transition = (old_rotation, self.rotation)

        # Получаем данные для wall kick
        kick_data = WALL_KICK_DATA["I"] if self.shape_name == "I" else WALL_KICK_DATA["default"]
        kicks = kick_data.get(transition, [(0, 0)])

        # Пробуем все возможные сдвиги
        for dx, dy in kicks:
            self.x = old_x + dx
            self.y = old_y + dy

            if self.is_valid_position():
                return True  # Вращение успешно

        # Если ни один вариант не подошел - откатываем
        self.rotation = old_rotation
        self.x, self.y = old_x, old_y
        return False
    
    def lock(self):
        for x, y in self.get_cells():
            self.board.grid[y][x] = 1  # Блок занят
            self.board.colors[y][x] = self.color

    def move(self, dx, dy):
        if self.is_valid_position(dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False
    
    def hard_drop(self):
        while self.move(0, 1):
            pass
        self.lock()

    def get_cells(self):
        cells = []
        shape = self.shape
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    cells.append((self.x + col_idx, self.y + row_idx))
        return cells
    
    def draw(self, surface):
        shape = self.shape
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell and self.y + row_idx >= 0:
                    pygame.draw.rect(
                        surface,
                        self.color,
                        (
                            self.board.x + (self.x + col_idx) * self.block_size + 1,
                            self.board.y + (self.y + row_idx) * self.block_size + 1,
                            self.block_size - 1,
                            self.block_size - 1,
                        ),
                    )
    