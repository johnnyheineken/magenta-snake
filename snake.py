"""Snake implemented with pyxel.

This is the game of snake in pyxel version!

Try and collect the tasty apples without running
into the side or yourself.

Controls are the arrow keys ← ↑ → ↓

Q: Quit the game
R: Restart the game

Created by Marcus Croucher in 2018.
"""
import logging
from collections import deque, namedtuple

import pyxel

from dataclasses import dataclass

SCALING_RATIO = 4


@dataclass
class Point:
    x: int
    y: int

    @property
    def draw_x(self):
        return self.x * SCALING_RATIO

    @property
    def draw_y(self):
        return self.y * SCALING_RATIO

    def __repr__(self):
        return f"Point({self.x}, {self.y}))"

    def __hash__(self):
        return 1000 * self.x + self.y


# Point = namedtuple("Point", ["x", "y"])  # Convenience class for coordinates

#############
# Constants #
#############

COL_MAGENTA = pyxel.COLOR_RED
COL_LIGHT_YELLOW = pyxel.COLOR_YELLOW
COL_ORANGE = pyxel.COLOR_ORANGE
COL_BLUE = pyxel.COLOR_NAVY
COL_WHITE = pyxel.COLOR_WHITE
COL_BLACK = pyxel.COLOR_BLACK
COL_GREEN = pyxel.COLOR_GREEN
COL_PINK = pyxel.COLOR_PINK

TEXT_DEATH = ["GAME OVER", "(R)ESTART"]
HEIGHT_DEATH = 5

WIDTH = 30
HEIGHT = 45

DRAW_WIDTH = SCALING_RATIO * WIDTH
DRAW_HEIGHT = SCALING_RATIO * HEIGHT

HEIGHT_SCORE = pyxel.FONT_HEIGHT
HEIGHT_CONTROLS = HEIGHT_SCORE * 2

UP = Point(0, -1)
DOWN = Point(0, 1)
RIGHT = Point(1, 0)
LEFT = Point(-1, 0)

START = Point(5, 5 + HEIGHT_SCORE)

SCORE_SPEED = {
    0: 18,
    2: 16,
    5: 14,
    9: 12,
    12: 10,
    17: 9,
    23: 8,
    30: 7,
    38: 6,
    49: 5,
    60: 4,
    75: 3,
    88: 2,
    99: 1

}

DEFAULT_SPEED = 20
MAX_TIME_BONUS = 300
MAX_SECONDS_PER_POINT = 3
COLLISION_WITH_WALLS = False

SPEED_TO_FRAME_MAPPING = {
    20: [8, 7, 7],
    19: [7, 7, 7],
    18: [7, 7, 6],
    17: [7, 6, 6],
    16: [6, 6, 6],
    15: [6, 6, 5],
    14: [6, 5, 5],
    13: [5, 5, 5],
    12: [5, 5, 4],
    11: [5, 4, 4],
    10: [4, 4, 4],
    9: [4, 4, 3],
    8: [4, 3, 3],
    7: [3, 3, 3],
    6: [3, 3, 2],
    5: [3, 2, 2],
    4: [2, 2, 2],
    3: [2, 2, 1],
    2: [2, 1, 1],
    1: [1, 1, 1]
}


###################
# The game itself #
###################

def define_colors():
    pyxel.colors[COL_MAGENTA] = 0xCC0066
    # pyxel.colors[COL_LIGHT_YELLOW] = 0xC97D23
    # pyxel.colors[COL_ORANGE] = 0xD0953B
    # pyxel.colors[COL_BLUE] = 0x4b34a3
    # pyxel.colors[COL_BLACK] = 0x000000
    # pyxel.colors[COL_WHITE] = 0xffffff
    # pyxel.colors[COL_GREEN] = 0x74b2b2
    # pyxel.colors[COL_PINK] = 0xc43486


logging.basicConfig(filename='snake_game.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class Snake:
    """The class that sets up and runs the game."""

    def __init__(self):
        """Initiate pyxel, set up initial game variables, and run."""

        pyxel.init(
            DRAW_WIDTH, DRAW_HEIGHT, title="Snake!", fps=60, display_scale=8, capture_scale=6
        )
        pyxel.load('assets.pyxres')
        define_colors()
        define_sound_and_music()
        self.wall_collision = COLLISION_WITH_WALLS
        self.reset()

        pyxel.mouse(visible=True)
        pyxel.run(self.update, self.draw)

    def reset(self):
        """Initiate key variables (direction, snake, apple, score, etc.)"""

        self.direction = RIGHT
        self.popped_point = None
        self.popped_point_1 = None
        self.popped_point_2 = None
        self.snake = deque()
        self.snake.append(START)
        self.apple = None
        self.death = False
        self.melons = 0
        self.apples = 0
        self.score = 0
        self.time_bonus = 0
        self.last_eaten_frame = 0
        self.generate_fruit()
        self.speed = DEFAULT_SPEED
        self.speed_frames = deque(SPEED_TO_FRAME_MAPPING[self.speed])
        self.current_frame_speed = self.speed_frames[0]
        self.frame_count = 0
        self.last_update_before = 0
        self.mouse_pressed_button = None
        self.debug_mode = False
        self.last_inputs = deque(maxlen=10)  # Store last 10 inputs for debugging
        self.frame_history = deque(maxlen=60)  # Store last 60 frames of snake positions
        logging.info("Game initialized")

        pyxel.playm(0, loop=True)

    ##############
    # Game logic #
    ##############
    def rotate_speed(self):
        self.speed_frames.rotate()
        self.current_frame_speed = self.speed_frames[0]
        self.last_update_before = 0

    def update(self):
        self.frame_count += 1
        self.last_update_before += 1

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.check_button_hitboxes()

        if not self.death:
            self.update_direction()
            if self.last_update_before == self.current_frame_speed:
                self.rotate_speed()
                self.update_snake()
                self.check_death()
                self.check_fruit()

                # Log snake position every frame
                self.frame_history.append(list(self.snake))
                logging.debug(f"Frame {self.frame_count}: Snake positions: {list(self.snake)}")
        else:
            if self.mouse_pressed_button == 'up':
                self.reset()

        # Debug options
        if pyxel.btnp(pyxel.KEY_D):
            self.debug_mode = not self.debug_mode
            logging.info(f"Debug mode {'enabled' if self.debug_mode else 'disabled'}")

        if pyxel.btnp(pyxel.KEY_L):
            self.log_game_state()

        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()

        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
            self.reset()

    def check_button_hitboxes(self):
        x = pyxel.mouse_x
        y = pyxel.mouse_y
        button_height = HEIGHT_CONTROLS * SCALING_RATIO // 2 - 1
        button_width = DRAW_WIDTH // 3 - 2

        upper_row_high = DRAW_HEIGHT + 1 - HEIGHT_CONTROLS * SCALING_RATIO
        upper_row_low = upper_row_high + button_height

        lower_row_high = DRAW_HEIGHT + 1 - HEIGHT_CONTROLS * SCALING_RATIO // 2
        lower_row_low = lower_row_high + button_height

        first_col_left = 2
        first_col_right = first_col_left + button_width

        second_col_left = DRAW_WIDTH // 3 + 1
        second_col_right = second_col_left + button_width

        third_col_left = 2 * DRAW_WIDTH // 3
        third_col_right = third_col_left + button_width

        hitboxes = dict(
            up=[upper_row_high, upper_row_low, second_col_left, second_col_right],
            down=[lower_row_high, lower_row_low, second_col_left, second_col_right],
            left=[lower_row_high, lower_row_low, first_col_left, first_col_right],
            right=[lower_row_high, lower_row_low, third_col_left, third_col_right])
        for key, hitbox in hitboxes.items():
            if (hitbox[2] < x < hitbox[3]) & (hitbox[0] < y < hitbox[1]):
                print(key)
                self.mouse_pressed_button = key

        return None

    def update_direction(self):
        """Watch the keys and change direction."""
        previous_direction = self.direction
        if self.mouse_pressed_button:
            match self.mouse_pressed_button:
                case 'up':
                    if self.direction is not DOWN:
                        self.direction = UP
                case 'down':
                    if self.direction is not UP:
                        self.direction = DOWN
                case 'left':
                    if self.direction is not RIGHT:
                        self.direction = LEFT
                case 'right':
                    if self.direction is not LEFT:
                        self.direction = RIGHT
            self.mouse_pressed_button = None
        else:
            if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
                if self.direction is not DOWN:
                    self.direction = UP
            elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
                if self.direction is not UP:
                    self.direction = DOWN
            elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
                if self.direction is not RIGHT:
                    self.direction = LEFT
            elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
                if self.direction is not LEFT:
                    self.direction = RIGHT

        # Log direction changes
        if self.direction != previous_direction:
            logging.info(f"Direction changed from {previous_direction} to {self.direction}")

        # Store input for debugging
        self.last_inputs.append(self.direction)

    def get_new_snake_head(self):
        old_head = self.snake[0]

        if self.wall_collision is False:
            if old_head.x < 0:
                return Point(WIDTH - 1, old_head.y + self.direction.y)
            elif old_head.x >= WIDTH:
                return Point(0, old_head.y + self.direction.y)
            elif old_head.y < HEIGHT_SCORE:
                return Point(old_head.x + self.direction.x, HEIGHT - HEIGHT_CONTROLS - 1)
            elif old_head.y >= HEIGHT - HEIGHT_CONTROLS:
                return Point(old_head.x + self.direction.x, HEIGHT_SCORE)

        return Point(old_head.x + self.direction.x, old_head.y + self.direction.y)

    def update_snake(self):
        """Move the snake based on the direction."""
        new_head = self.get_new_snake_head()
        self.snake.appendleft(new_head)
        self.popped_point_2 = self.popped_point_1
        self.popped_point_1 = self.popped_point
        self.popped_point = self.snake.pop()

    def check_fruit(self):
        if SCORE_SPEED.get(self.melons + self.apples) is not None:
            self.check_melon()
        else:
            self.check_apple()
    def add_time_bonus(self):
        self.time_bonus += min(max(MAX_SECONDS_PER_POINT * 60 + self.last_eaten_frame - self.frame_count, 0), MAX_TIME_BONUS)
        self.last_eaten_frame = self.frame_count
    def check_melon(self):
        if {self.snake[0]}.intersection(set(self.melon)):

            self.speed = SCORE_SPEED[self.melons + self.apples]
            self.melons += 1
            self.score += 3

            self.add_time_bonus()
            self.generate_fruit()
            self.snake.append(self.popped_point)
            self.snake.append(self.popped_point_1)
            self.snake.append(self.popped_point_2)

            self.speed_frames = deque(SPEED_TO_FRAME_MAPPING[self.speed])
            pyxel.play(0, 0)

    def check_apple(self):
        """Check whether the snake is on an apple."""

        if self.snake[0] == self.apple:
            self.apples += 1
            self.score += 1
            self.add_time_bonus()
            self.snake.append(self.popped_point)
            self.generate_fruit()

            pyxel.play(0, 0)

    def generate_fruit(self):
        if SCORE_SPEED.get(self.melons + self.apples) is not None:
            self.generate_melon()
        else:
            self.generate_apple()

    def generate_apple(self):
        """Generate an apple randomly."""
        snake_pixels = set(self.snake)

        self.apple = self.snake[0]
        while self.apple in snake_pixels:
            x = pyxel.rndi(0, WIDTH - 1)
            y = pyxel.rndi(HEIGHT_SCORE + 1, HEIGHT - HEIGHT_CONTROLS - 1)
            self.apple = Point(x, y)

    def melon_points(self, x, y):
        return [Point(x, y), Point(x + 1, y), Point(x, y + 1), Point(x + 1, y + 1)]

    def generate_melon(self):
        """Generate an apple randomly."""
        snake_pixels = set(self.snake)

        self.melon = self.melon_points(self.snake[0].x, self.snake[0].y)
        while set(self.melon).intersection(snake_pixels):
            x = pyxel.rndi(0, WIDTH - 2)
            y = pyxel.rndi(HEIGHT_SCORE + 2, HEIGHT - HEIGHT_CONTROLS - 2)
            self.melon = self.melon_points(x, y)

    # def check_death(self):
    #     """Check whether the snake has died (out of bounds or doubled up.)"""
    #
    #     head = self.snake[0]
    #     if self.wall_collision:
    #         if head.x < 0 or head.y < HEIGHT_SCORE or head.x >= WIDTH or head.y >= HEIGHT - HEIGHT_CONTROLS:
    #             self.death_event()
    #     if len(self.snake) != len(set(self.snake)):
    #         self.death_event()

    # def death_event(self):
    #     """Kill the game (bring up end screen)."""
    #     self.death = True  # Check having run into self
    #
    #     pyxel.stop()
    #     pyxel.play(0, 1)

    ##############
    # Draw logic #
    ##############

    def draw(self):
        if not self.death:
            pyxel.cls(col=COL_BLACK)
            self.draw_snake()
            self.draw_score()
            self.draw_fruit()
            self.draw_controls()

            # Draw debug information
            if self.debug_mode:
                self.draw_debug_info()
        else:
            self.draw_death()

    def draw_fruit(self):
        if SCORE_SPEED.get(self.melons + self.apples) is not None:
            self.draw_melon()
        else:
            self.draw_apple()

    def draw_apple(self):
        # pyxel.rect(self.apple.draw_x, self.apple.draw_y, w=SCALING_RATIO, h=SCALING_RATIO, col=COL_WHITE)
        # pyxel.rectb(self.apple.draw_x, self.apple.draw_y, w=SCALING_RATIO, h=SCALING_RATIO, col=COL_LIGHT_YELLOW)
        pyxel.blt(self.apple.draw_x - 2, self.apple.draw_y - 2, 0, 0, 0, 8, 8, colkey=pyxel.COLOR_BLACK)
        # pyxel.rect(self.apple.draw_x, self.apple.draw_y, w=SCALING_RATIO, h=SCALING_RATIO, col=COL_WHITE)

        # greenery_offset = SCALING_RATIO // 2
        # pyxel.pset(self.apple.draw_x + greenery_offset, self.apple.draw_y - 1, COL_GREEN)
        # pyxel.pset(self.apple.draw_x + greenery_offset + 1, self.apple.draw_y - 2, COL_GREEN)
        # pyxel.pset(self.apple.draw_x, self.apple.draw_y, col=COL_MAGENTA)

    def draw_melon(self):
        pyxel.blt(self.melon[0].draw_x - 4, self.melon[0].draw_y - 4, 0, 16, 0, 16, 16, colkey=pyxel.COLOR_BLACK)
        # pyxel.rect(self.melon[0].draw_x, self.melon[0].draw_y, w=SCALING_RATIO * 2, h=SCALING_RATIO * 2, col=COL_GREEN)

    def draw_snake(self):
        """Draw the snake with a distinct head by iterating through deque."""

        for i, point in enumerate(self.snake):
            if i == 0:
                colour = pyxel.COLOR_GREEN
            else:
                colour = pyxel.COLOR_LIME

            pyxel.rect(point.draw_x, point.draw_y, w=SCALING_RATIO, h=SCALING_RATIO, col=colour)

    def draw_score(self):
        """Draw the score at the top."""

        score = f"{self.score * 100 + self.time_bonus:04}"
        pyxel.rect(0, 0, DRAW_WIDTH, HEIGHT_SCORE * SCALING_RATIO, COL_MAGENTA)
        pyxel.text(1, 1, score, COL_WHITE)

    def draw_controls(self):
        """Draw the score at the top."""

        pyxel.rect(x=0,
                   y=DRAW_HEIGHT - HEIGHT_CONTROLS * SCALING_RATIO,
                   w=DRAW_WIDTH,
                   h=HEIGHT_CONTROLS * SCALING_RATIO,
                   col=COL_MAGENTA)
        button_width = DRAW_WIDTH // 3 - 2
        button_height = HEIGHT_CONTROLS * SCALING_RATIO // 2 - 1
        upper_row = DRAW_HEIGHT + 1 - HEIGHT_CONTROLS * SCALING_RATIO
        lower_row = DRAW_HEIGHT + 1 - HEIGHT_CONTROLS * SCALING_RATIO // 2
        button_color = pyxel.COLOR_WHITE
        self.draw_button(DRAW_WIDTH // 3 + 1,
                         y=upper_row,
                         w=button_width,
                         h=button_height,
                         col=button_color, text='UP', text_col=COL_BLACK, pressed_col=COL_PINK)
        self.draw_button(DRAW_WIDTH // 3 + 1,
                         y=lower_row,
                         w=button_width,
                         h=button_height,
                         col=button_color, text='DOWN', text_col=COL_BLACK, pressed_col=COL_PINK)
        self.draw_button(2,
                         y=lower_row,
                         w=button_width,
                         h=button_height,
                         col=button_color, text='LEFT', text_col=COL_BLACK, pressed_col=COL_PINK)
        self.draw_button(2 * DRAW_WIDTH // 3,
                         y=lower_row,
                         w=button_width,
                         h=button_height,
                         col=button_color, text='RIGHT', text_col=COL_BLACK, pressed_col=COL_PINK)

    def draw_button(self, x, y, w, h, col, text, text_col, pressed_col):
        if text.lower == self.mouse_pressed_button:
            col = pressed_col
        pyxel.rect(x, y, w, h, col)
        text_x = self.center_button_text(text, x, w)
        text_y = self.center_button_text_vertically(y, h)
        pyxel.text(text_x, text_y, text, text_col)

    def draw_death(self):
        """Draw a blank screen with some text."""

        pyxel.cls(col=COL_WHITE)
        display_text = TEXT_DEATH[:-1]
        display_text.append(' ')
        display_text.append('FRUIT')
        display_text.append(f"{self.score * 100:04}")
        display_text.append(' ')
        display_text.append('TIME BONUS')
        display_text.append(f'{self.time_bonus:04}')
        display_text.append('-----')
        display_text.append(f"{self.score * 100 + self.time_bonus:03}")
        for i, text in enumerate(display_text):
            y_offset = (pyxel.FONT_HEIGHT + 2) * i
            text_x = self.center_text(text, DRAW_WIDTH)
            pyxel.text(text_x, HEIGHT_DEATH + y_offset, text, COL_MAGENTA)

        x = DRAW_WIDTH // 3 + 1
        y = DRAW_HEIGHT + 1 - HEIGHT_CONTROLS * SCALING_RATIO
        button_width = DRAW_WIDTH // 3 - 2
        button_height = HEIGHT_CONTROLS * SCALING_RATIO // 2 - 1

        self.draw_button(x, y, w=button_width, h=button_height, col=COL_BLACK, text=TEXT_DEATH[-1], text_col=COL_WHITE,
                         pressed_col=COL_GREEN)

    @staticmethod
    def center_text(text, page_width, char_width=pyxel.FONT_WIDTH):
        """Helper function for calculating the start x value for centered text."""

        text_width = len(text) * char_width
        return (page_width - text_width) // 2

    @staticmethod
    def center_button_text(text, button_x, button_width, char_width=pyxel.FONT_WIDTH):
        """Helper function for calculating the start x value for centered text."""

        text_width = len(text) * char_width

        return button_x + (button_width - text_width) // 2

    @staticmethod
    def center_button_text_vertically(button_y, button_height, char_height=pyxel.FONT_HEIGHT):
        """Helper function for calculating the start x value for centered text."""

        return button_y + (button_height - char_height) // 2

    def check_death(self):
        head = self.snake[0]
        if self.wall_collision:
            if head.x < 0 or head.y < HEIGHT_SCORE or head.x >= WIDTH or head.y >= HEIGHT - HEIGHT_CONTROLS:
                logging.warning(f"Death by wall collision at position {head}")
                self.death_event()
        if len(self.snake) != len(set(self.snake)):
            logging.warning(f"Death by self-collision at position {head}")
            self.death_event()

    def death_event(self):
        self.death = True
        logging.critical(f"Game over at frame {self.frame_count}")
        logging.info(f"Last 10 inputs: {list(self.last_inputs)}")
        logging.info(f"Last 60 frames of snake positions: {list(self.frame_history)}")
        pyxel.stop()
        pyxel.play(0, 1)

    def log_game_state(self):
        logging.info(f"Current game state:")
        logging.info(f"Score: {self.score}")
        logging.info(f"Snake length: {len(self.snake)}")
        logging.info(f"Snake head position: {self.snake[0]}")
        logging.info(f"Apple position: {self.apple}")
        logging.info(f"Current speed: {self.speed}")
        logging.info(f"Frame count: {self.frame_count}")



    def draw_debug_info(self):
        pyxel.text(1, HEIGHT_SCORE * SCALING_RATIO + 1, f"Frame: {self.frame_count}", pyxel.COLOR_GRAY)
        pyxel.text(1, HEIGHT_SCORE * SCALING_RATIO + 9, f"Speed: {self.speed}", pyxel.COLOR_GRAY)
        pyxel.text(1, HEIGHT_SCORE * SCALING_RATIO + 17, f"Head: {self.snake[0]}", pyxel.COLOR_GRAY)


###########################
# Music and sound effects #
###########################


def define_sound_and_music():
    """Define sound and music."""

    # Sound effects
    pyxel.sounds[0].set(
        notes="c3e3g3c4c4", tones="s", volumes="4", effects=("n" * 4 + "f"), speed=7
    )
    pyxel.sounds[1].set(
        notes="f3 b2 f2 b1  f1 f1 f1 f1",
        tones="p",
        volumes=("4" * 4 + "4321"),
        effects=("n" * 7 + "f"),
        speed=9,
    )

    melody1 = (
            "c3 c3 c3 d3 e3 r e3 r"
            + ("r" * 8)
            + "e3 e3 e3 f3 d3 r c3 r"
            + ("r" * 8)
            + "c3 c3 c3 d3 e3 r e3 r"
            + ("r" * 8)
            + "b2 b2 b2 f3 d3 r c3 r"
            + ("r" * 8)
    )

    melody2 = (
            "rrrr e3e3e3e3 d3d3c3c3 b2b2c3c3"
            + "a2a2a2a2 c3c3c3c3 d3d3d3d3 e3e3e3e3"
            + "rrrr e3e3e3e3 d3d3c3c3 b2b2c3c3"
            + "a2a2a2a2 g2g2g2g2 c3c3c3c3 g2g2a2a2"
            + "rrrr e3e3e3e3 d3d3c3c3 b2b2c3c3"
            + "a2a2a2a2 c3c3c3c3 d3d3d3d3 e3e3e3e3"
            + "f3f3f3a3 a3a3a3a3 g3g3g3b3 b3b3b3b3"
            + "b3b3b3b4 rrrr e3d3c3g3 a2g2e2d2"
    )

    # Music
    pyxel.sounds[2].set(
        notes=melody1 * 2 + melody2 * 2,
        tones="s",
        volumes=("3"),
        effects=("nnnsffff"),
        speed=20,
    )

    harmony1 = (
            "a1 a1 a1 b1  f1 f1 c2 c2"
            "c2 c2 c2 c2  g1 g1 b1 b1"
            * 3
            + "f1 f1 f1 f1 f1 f1 f1 f1 g1 g1 g1 g1 g1 g1 g1 g1"
    )
    harmony2 = (
            ("f1" * 8 + "g1" * 8 + "a1" * 8 + ("c2" * 7 + "d2")) * 3 + "f1" * 16 + "g1" * 16
    )

    pyxel.sounds[3].set(
        notes=harmony1 * 2 + harmony2 * 2, tones="t", volumes="5", effects="f", speed=20
    )
    pyxel.sounds[4].set(
        notes=("f0 r a4 r  f0 f0 a4 r" "f0 r a4 r   f0 f0 a4 f0"),
        tones="n",
        volumes="6622 6622 6622 6426",
        effects="f",
        speed=20,
    )

    pyxel.musics[0].set([], [2], [3], [4])


Snake()
