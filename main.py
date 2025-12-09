from random import shuffle
from math import sqrt, floor

import pygame
import pygame_widgets

from pygame_widgets.button import Button

from tetromino import Tetromino
from board import Board


from config import (
    WIDTH,
    HEIGHT,
    FPS,
    FONT_SIZE,
    FONT_NAME,
    HORIZONTAL_MARGIN_RATIO,
    VERTICAL_MARGIN_RATIO,
    BOARD_SIZE,
    HOLD_BOARD_SIZE,
    NUM_NEXT_BLOCKS,
    NEXT_BOARD_SIZE,
    SCORE_DATA,
    MAX_LEVEL,
    TETROMINOS,
    SOFT_DROP_DELAY,
    DAS_DELAY,
    ARR_DELAY,
    HEADERS_COLOR,
    STATS_COLOR,
    BOARD_LINE_COLOR,
    STATS_BOX_PADDING,
    BACKGROUND_COLOR,
)


# TODO: add animations
# TODO: add music and sound effects
# TODO: add pause functionality
# TODO: add start screen and game over screen
# TODO: add high score tracking
# TODO: add settings menu


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
        block_size = (
            sqrt(
                (WIDTH - 2 * horizontal_margin)
                * (HEIGHT - vertical_margin)
                / (BOARD_SIZE[0] * BOARD_SIZE[1])
            )
        )
        self.board = Board(
            x=horizontal_margin,
            y=vertical_margin,
            block_size=block_size,
            board_size=BOARD_SIZE,
        )

        self.hold_board = Board(
            x=horizontal_margin / 2 - HOLD_BOARD_SIZE[0] * block_size / 2,
            y=vertical_margin,
            block_size=block_size,
            board_size=HOLD_BOARD_SIZE,
        )

        self.next_board = Board(
            x=WIDTH - horizontal_margin / 2 - NEXT_BOARD_SIZE[0] * block_size / 2,
            y=vertical_margin,
            block_size=block_size,
            board_size=NEXT_BOARD_SIZE,
        )

        self.tetrominos = []
        self.tetromino = None
        self.hold = None
        self.hold_swapped = False

        self.soft_drop = False
        self.last_move_time = 0
        self.move_held_time = 0
        self.held_direction = 0

        self.is_new_game = True
        self.is_paused = True
        self.pause_surface = pygame.Surface((WIDTH, HEIGHT))
        self.pause_surface.fill((128, 128, 128))
        self.pause_surface.set_alpha(128)
        self.game_over = False
        self.total_lines_cleared = 0
        self.score = 0
        self.level = 0

        # Texts
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.score_render = self.font.render(f"Score: {self.score}", 0, STATS_COLOR)
        self.level_render = self.font.render(f"Level: {self.level + 1}", 0, STATS_COLOR)
        self.lines_render = self.font.render(
            f"Lines: {self.total_lines_cleared}", 0, STATS_COLOR
        )

        box_width = (
            self.hold_board.width * self.hold_board.block_size * 2
            + STATS_BOX_PADDING * 2
        )
        box_height = (
            self.score_render.get_height()
            + self.level_render.get_height()
            + self.lines_render.get_height()
            + STATS_BOX_PADDING * 4
        )
        self.stats_box = pygame.Rect(
            horizontal_margin / 2 - box_width / 2,
            HEIGHT
            - (self.hold_board.y + self.hold_board.height * self.hold_board.block_size)
            - box_height,
            box_width,
            box_height,
        )
        self.tetris_render = self.font.render("TETRIS", 1, HEADERS_COLOR)
        self.hold_render = self.font.render("HOLD", 1, HEADERS_COLOR)
        self.next_render = self.font.render("NEXT", 1, HEADERS_COLOR)

        button_width = WIDTH * 0.3
        button_height = HEIGHT * 0.1
        self.start_button = Button(
            self.win,
            WIDTH / 2 - button_width / 2,
            HEIGHT / 2 - button_height / 2 - 10 - button_height,
            button_width,
            button_height,
            text="PLAY",
            radius=20,
            font=self.font,
            onClick=self.pause,
        )
        self.settings_button = Button(
            self.win,
            WIDTH / 2 - button_width / 2,
            HEIGHT / 2 - button_height / 2,
            button_width,
            button_height,
            text="SETTINGS",
            radius=20,
            font=self.font,
        )

        self.exit_button = Button(
            self.win,
            WIDTH / 2 - button_width / 2,
            HEIGHT / 2 + button_height / 2 + 10,
            button_width,
            button_height,
            text="EXIT",
            radius=20,
            font=self.font,
            onClick=self.stop_game,
        )

        pygame.display.set_caption("TETRIS")

    def run(self):
        while self.running:
            if not self.tetromino:
                self.tetromino = self.get_tetromino()

            self.check_events()
            self.update_window()
            self.clock.tick(FPS)
            
            if self.is_paused:
                # self.main_menu()
                continue

            if self.game_over:
                self.stop_game()
                continue

            block_locked, lock_above = self.tetromino.fall()
            if block_locked:
                self.tetromino = self.get_tetromino()
            if lock_above:
                self.game_over = True
                continue

            self._handle_das_arr()
            self.calculate_score()
            self.check_level_up()
            
        pygame.quit()

    def check_tetromino_keydown_event(self, event: pygame.event.Event):
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.held_direction = -1
            self.move_held_time = pygame.time.get_ticks() / 1000
            self.tetromino.move(-1, 0)
            self.last_move_time = self.move_held_time
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.held_direction = 1
            self.move_held_time = pygame.time.get_ticks() / 1000
            self.tetromino.move(1, 0)
            self.last_move_time = self.move_held_time

        elif event.key in (pygame.K_DOWN, pygame.K_s):
            if not self.soft_drop:
                self.soft_drop = True
                self.tetromino.set_fall_delay(SOFT_DROP_DELAY)

        elif event.key == pygame.K_SPACE:
            lock_above = self.tetromino.hard_drop()
            if lock_above:
                self.game_over = True
            else:
                self.tetromino = self.get_tetromino()

        elif event.key == pygame.K_UP:
            self.tetromino.rotate(1)
        elif event.key == pygame.K_z:
            self.tetromino.rotate(-1)

        elif event.key == pygame.K_c:
            if not self.hold_swapped:
                self.swap_hold()

    def check_tetromino_keyup_event(self, event: pygame.event.Event):
        if event.key in (pygame.K_DOWN, pygame.K_s):
                self.soft_drop = False
                self.tetromino.reset_fall_delay()
        elif (
            event.key in (pygame.K_LEFT, pygame.K_a)
            and self.held_direction == -1
        ):
            self.held_direction = 0
        elif (
            event.key in (pygame.K_RIGHT, pygame.K_d)
            and self.held_direction == 1
        ):
            self.held_direction = 0

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause()
                    self.soft_drop = False
                    self.held_direction = 0
                    self.last_move_time = 0
                    self.move_held_time = 0
                    self.tetromino.reset_fall_delay()
                    # pygame.event.clear()
                    # break

                if not self.is_paused:
                    self.check_tetromino_keydown_event(event)

            if event.type == pygame.KEYUP:
                if not self.is_paused:
                    self.check_tetromino_keyup_event(event)            

    def update_window(self):
        self.win.fill(BACKGROUND_COLOR)

        self.print_headers()
        self.print_stats()

        self.board.draw(self.win)
        self.hold_board.draw(self.win)
        self.next_board.draw(self.win)

        self.tetromino.draw(self.win)

        if self.is_paused:
            self.win.blit(self.pause_surface, (0, 0))
            pygame_widgets.update(pygame.event.get())

        pygame.display.flip()

    def main_menu(self):
        pass

    def get_tetromino(self):
        if len(self.tetrominos) < 7:
            # Refill the bag if there are less than 7 tetrominos left
            # 7 because there are 7 unique tetrominos
            new_bag = list(TETROMINOS.keys())
            shuffle(new_bag)
            self.tetrominos.extend(new_bag)

        tetromino_name = self.tetrominos.pop(0)

        self.next_board.reset()

        for idx, shape_name in enumerate(self.tetrominos[:NUM_NEXT_BLOCKS]):
            temp_tetromino = Tetromino(shape_name=shape_name, board=self.board)
            temp_tetromino.swap_board(self.next_board, y=idx * 4 + 1, lock=True)

        self.hold_swapped = False
        if self.soft_drop:
            self.soft_drop = False
            pygame.event.post(
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
            )  # Simulate soft drop key press to reset state
        return Tetromino(shape_name=tetromino_name, board=self.board, level=self.level)

    def check_level_up(self):
        new_level = self.total_lines_cleared // 10
        self.level = min(new_level, MAX_LEVEL)
        self.level_render = self.font.render(f"Level: {self.level + 1}", 0, STATS_COLOR)

    def calculate_score(self):
        update_score = False
        if self.soft_drop and self.tetromino.lock_start == 0:
            self.score += 1  # 1 point per soft drop cell
            update_score = True
        lines = self.board.check_lines()
        if lines > 0:
            self.total_lines_cleared += lines
            self.score += SCORE_DATA[lines] * (self.level + 1)
            update_score = True
            self.lines_render = self.font.render(
                f"Lines: {self.total_lines_cleared}", 0, STATS_COLOR
            )
        if update_score:
            self.score_render = self.font.render(f"Score: {self.score}", 0, STATS_COLOR)

    def swap_hold(self):
        if self.hold is None:
            self.hold = self.tetromino
            self.hold.swap_board(self.hold_board, y=1, lock=True)

            self.tetromino = self.get_tetromino()
        else:
            self.hold, self.tetromino = self.tetromino, self.hold

            self.hold.swap_board(self.hold_board, y=1, board_reset=True, lock=True)

            self.tetromino.swap_board(self.board)
        self.hold_swapped = True

    def _handle_das_arr(self):
        if self.held_direction == 0:
            return

        current_time = pygame.time.get_ticks() / 1000

        if current_time - self.move_held_time >= DAS_DELAY:

            if current_time - self.last_move_time >= ARR_DELAY:

                # Выполняем движение и сбрасываем ARR таймер
                self.tetromino.move(self.held_direction, 0)
                self.last_move_time = current_time

    def print_stats(self):
        pygame.draw.rect(self.win, BOARD_LINE_COLOR, self.stats_box, width=1)

        self.win.blit(
            self.score_render,
            (
                self.stats_box.x + STATS_BOX_PADDING,
                self.stats_box.y + STATS_BOX_PADDING,
            ),
        )
        self.win.blit(
            self.level_render,
            (
                self.stats_box.x + STATS_BOX_PADDING,
                self.stats_box.y
                + STATS_BOX_PADDING * 2
                + self.score_render.get_height(),
            ),
        )
        self.win.blit(
            self.lines_render,
            (
                self.stats_box.x + STATS_BOX_PADDING,
                self.stats_box.y
                + STATS_BOX_PADDING * 3
                + self.score_render.get_height()
                + self.level_render.get_height(),
            ),
        )

    def print_headers(self):
        self.win.blit(
            self.tetris_render,
            (
                self.board.x
                + (
                    self.board.width * self.board.block_size
                    - self.tetris_render.get_width()
                )
                / 2,
                self.board.y - self.tetris_render.get_height(),
            ),
        )
        self.win.blit(
            self.hold_render,
            (
                self.hold_board.x
                + (
                    self.hold_board.width * self.hold_board.block_size
                    - self.hold_render.get_width()
                )
                / 2,
                self.hold_board.y - self.hold_render.get_height(),
            ),
        )
        self.win.blit(
            self.next_render,
            (
                self.next_board.x
                + (
                    self.next_board.width * self.next_board.block_size
                    - self.next_render.get_width()
                )
                / 2,
                self.next_board.y - self.next_render.get_height(),
            ),
        )

    def pause(self):
        self.is_paused = not self.is_paused

    def stop_game(self):
        self.running = False


if __name__ == "__main__":
    game = Game()
    game.run()
