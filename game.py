import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

# Initialize Pygame
pygame.init()
font = pygame.font.Font(None, 25)  # Use default font

# Enum for direction
class Direction(Enum):
    RIGHT = 1  # Right
    LEFT = 2   # Left
    UP = 3     # Up
    DOWN = 4   # Down

# Namedtuple for position (x, y)
Point = namedtuple('Point', 'x, y')

# RGB colors
WHITE = (255, 255, 255)  # White
RED = (200, 0, 0)        # Red
BLUE1 = (0, 0, 255)      # Dark blue
BLUE2 = (0, 100, 255)    # Light blue
GREEN = (52, 118, 105)   # Dark green
GREEN2 = (124, 252, 0)   # Light green
BLACK = (0, 0, 0)        # Black

# Block size and speed
BLOCK_SIZE = 20  # Size of each block
SPEED = 10       # Game speed

# SnakeGameAI class
class SnakeGameAI:
    def __init__(self, w=640, h=480):
        # Initialize game window and size
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        self.window = self.display
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # Reset game state
        self.direction = Direction.RIGHT  # Initial direction of snake 1
        self.direction2 = Direction.RIGHT  # Initial direction of snake 2
        self.head = Point(self.w / 2, self.h / 2)  # Initial position of snake 1
        self.snake = [self.head]  # Body of snake 1
        self.head2 = Point(self.w / 4, self.h / 4)  # Initial position of snake 2
        self.snake2 = [self.head2]  # Body of snake 2
        self.score = 0  # Score of snake 1
        self.score2 = 0  # Score of snake 2
        self.food = None  # Food position
        self._place_food()  # Place initial food
        self.frame_iteration = 0  # Frame counter

    def _place_food(self):
        # Randomize food position on the grid
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        # Ensure food is not placed on the snakes
        if self.food in self.snake or self.food in self.snake2:
            self._place_food()

    def play_step(self, action):
        # Increment frame counter
        self.frame_iteration += 1
        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                # Control snake 2 with WASD keys
                if event.key == pygame.K_a and self.direction2 != Direction.RIGHT:
                    self.direction2 = Direction.LEFT
                elif event.key == pygame.K_d and self.direction2 != Direction.LEFT:
                    self.direction2 = Direction.RIGHT
                elif event.key == pygame.K_w and self.direction2 != Direction.DOWN:
                    self.direction2 = Direction.UP
                elif event.key == pygame.K_s and self.direction2 != Direction.UP:
                    self.direction2 = Direction.DOWN
                # Adjust speed with arrow keys
                elif event.key == pygame.K_UP:  # Increase speed
                    self.change_speed(1)
                elif event.key == pygame.K_DOWN:  # Decrease speed
                    self.change_speed(-1)

        # Move snakes
        self._move(action)  # Move snake 1 based on AI action
        self.snake.insert(0, self.head)  # Add new head to snake 1
        self._move2(self.direction2)  # Move snake 2 based on user input
        self.snake2.insert(0, self.head2)  # Add new head to snake 2

        # Initialize reward, game over, and winner
        reward = 0
        game_over = False
        winner = None

        # Check for collisions
        if self.is_collision(self.head):
            game_over = True
            winner = "Player 1 ตาย! Player 2 ชนะ!"
        elif self.is_collision(self.head2):
            game_over = True
            winner = "Player 2 ตาย! Player 1 ชนะ!"

        # Check for head collision with the other snake's body
        if self.head in self.snake2[1:]:
            game_over = True
            winner = "Player 1 ชนะ!"
        elif self.head2 in self.snake[1:]:
            game_over = True
            winner = "Player 2 ชนะ!"

        # If game over, return the result
        if game_over:
            return reward, game_over, self.score, self.score2, winner

        # Check if snake 1 eats the food
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()  # Remove tail if no food is eaten

        # Check if snake 2 eats the food
        if self.head2 == self.food:
            self.score2 += 1
            self._place_food()
        else:
            self.snake2.pop()  # Remove tail if no food is eaten

        # Update UI and control time
        self._update_ui()
        self.clock.tick(SPEED)
        return reward, game_over, self.score, self.score2, winner

    def is_collision(self, pt=None):
        # Check if the position is out of bounds
        if pt is None:
            pt = self.head
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        return False

    def _update_ui(self):
        # Clear the screen
        self.display.fill(BLACK)
        # Draw snake 1
        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREEN2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        # Draw snake 2
        for pt in self.snake2:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        # Draw food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Display scores and speed
        text = font.render("score (AI): " + str(self.score), True, WHITE)
        text2 = font.render("score (player): " + str(self.score2), True, WHITE)
        speed_text = font.render("speed in dgame: " + str(SPEED), True, WHITE)  # Display speed
        self.display.blit(text, [0, 0])
        self.display.blit(text2, [0, 30])
        self.display.blit(speed_text, [0, 60])  # Display speed
        pygame.display.flip()

    def _move(self, action):
        # List of directions in clockwise order
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        # Determine new direction based on action
        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        # Update head position based on direction
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)

    def _move2(self, direction):
        # Update head position of snake 2 based on direction
        x = self.head2.x
        y = self.head2.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head2 = Point(x, y)

    def change_speed(self, delta):
        # Adjust game speed within bounds
        global SPEED
        SPEED = max(5, min(SPEED + delta, 30))  # Speed is between 5 and 30

# Main game loop
if __name__ == "__main__":
    game = SnakeGameAI()
    while True:
        action = [1, 0, 0]  # AI action (placeholder)
        reward, game_over, score, score2, winner = game.play_step(action)
        if game_over:
            print(winner)
            break
