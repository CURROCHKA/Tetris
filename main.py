from random import choice
from math import sqrt

import pygame

from tetromino import Tetromino
from board import Board


from config import (
    WIDTH,
    HEIGHT,
    FPS,
    HORIZONTAL_MARGIN_RATIO,
    VERTICAL_MARGIN_RATIO,
    BOARD_SIZE,
)


class Game:
    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        horizontal_margin = WIDTH / HORIZONTAL_MARGIN_RATIO
        vertical_margin = HEIGHT / VERTICAL_MARGIN_RATIO
        # Calculate block size to fit the board within the window with margins
        # 20x * 10x = S
        # x = sqrt(S / 200)
        block_size = round(sqrt((WIDTH - 2 * horizontal_margin) * (HEIGHT - vertical_margin) / (BOARD_SIZE[0] * BOARD_SIZE[1])))
        self.board = Board(
            x=horizontal_margin,
            y=vertical_margin,
            block_size=block_size,
            )

        self.tetromino = None
        self.game_over = False
        self.score = 0

        pygame.display.set_caption("TETRIS")

    def run(self):
        while self.running:
            if self.tetromino is None:
                if not self.game_over:
                    self.tetromino = self.get_tetromino()
                else:
                    pass

            if self.tetromino.fall():
                self.tetromino = self.get_tetromino()

            self.score += self.board.check_lines()
            self.check_events()
            self.update_window()
            self.clock.tick(FPS)  # Limit to 60 frames per second

        pygame.quit()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_LEFT:
                    self.tetromino.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.tetromino.move(1, 0)
                    
                elif event.key == pygame.K_DOWN:
                    self.tetromino.move(0, 1)
                elif event.key == pygame.K_SPACE:
                    self.tetromino.hard_drop()
                    self.tetromino = self.get_tetromino()

                elif event.key == pygame.K_UP:
                    self.tetromino.rotate(1)
                elif event.key == pygame.K_z:
                    self.tetromino.rotate(-1)

    def update_window(self):
        self.win.fill((0, 0, 0))  # Fill the window with black color
        self.board.draw(self.win)
        self.tetromino.draw(self.win)
        pygame.display.flip()  # Update the display

    def get_tetromino(self):
        return Tetromino(board=self.board)


if __name__ == "__main__":
    game = Game()
    game.run()
