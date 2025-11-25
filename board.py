import pygame

from config import (
    BOARD_SIZE,
    BOARD_BLOCK_COLOR,
    BOARD_LINE_COLOR,
    BOARD_LINE_THICKNESS,
)


class Board:
    def __init__(self, x: float, y: float, block_size: int):
        self.x = x
        self.y = y
        self.width, self.height = BOARD_SIZE
        self.block_size = block_size
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.colors = [[BOARD_BLOCK_COLOR for _ in range(self.width)] for _ in range(self.height)]

    def check_lines(self):
        lines_cleared = 0
        for row_idx in range(self.height - 1, -1, -1):
            if all(self.grid[row_idx]):
                lines_cleared += 1
                del self.grid[row_idx]
                del self.colors[row_idx]
                self.grid.insert(0, [0 for _ in range(self.width)])
                self.colors.insert(0, [BOARD_BLOCK_COLOR for _ in range(self.width)])
        return lines_cleared

    def draw(self, surface: pygame.Surface):
        self.draw_blocks(surface)
        self.draw_lines(surface)

    def draw_lines(self, surface: pygame.Surface):
        # Vertical lines
        for x in range(self.width + 1):
            pygame.draw.line(
                surface,
                BOARD_LINE_COLOR,
                (self.x + x * self.block_size, self.y),
                (self.x + x * self.block_size, self.y + self.height * self.block_size),
                width=BOARD_LINE_THICKNESS,
            )
        # Horizontal lines
        for y in range(self.height + 1):
            pygame.draw.line(
                surface,
                BOARD_LINE_COLOR,
                (self.x, self.y + y * self.block_size),
                (self.x + self.width * self.block_size, self.y + y * self.block_size),
                width=BOARD_LINE_THICKNESS,
            )        

    def draw_blocks(self, surface):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(
                    surface,
                    self.colors[y][x],
                    (
                        self.x + x * self.block_size,
                        self.y + y * self.block_size,
                        self.block_size,
                        self.block_size
                    ),
                )
