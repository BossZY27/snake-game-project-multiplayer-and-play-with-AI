import time
import pygame
import random
from enum import Enum
from collections import namedtuple
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess  # เพื่อรันไฟล์ Python อื่น

pygame.init()
font = pygame.font.SysFont('arial', 25)

# Enum สำหรับทิศทาง
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# สี
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
GREEN = (52, 118, 105)
GREEN2 = (124, 252, 0)
YELLOW = (255, 255, 0)
YELLOW2 = (255, 215, 0)
BLACK = (0, 0, 0)

# ขนาดบล็อกและความเร็ว
BLOCK_SIZE = 20
SPEED = 10

class SnakeGame:
    def __init__(self, w=640, h=480, time_limit=60):
        self.w = w
        self.h = h
        self.time_limit = time_limit
        # เริ่มต้นหน้าจอ
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake Game - Two Players')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # เริ่มต้นสถานะเกม
        self.direction = Direction.RIGHT
        self.direction2 = Direction.LEFT
        self.head = Point(self.w / 4, self.h / 4)
        self.head2 = Point(self.w * 3 / 4, self.h * 3 / 4)
        self.snake = [self.head]
        self.snake2 = [self.head2]
        self.score = 0
        self.score2 = 0  # คะแนนของงูตัวที่ 2
        self.food = None
        self.start_time = time.time()
        self._place_food()

    def _place_food(self):
        # สุ่มตำแหน่งอาหาร
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake or self.food in self.snake2:
            self._place_food()

    def play_step(self):
        # 1. รับอินพุตจากผู้ใช้
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                # ควบคุมงูตัวที่ 1 (ลูกศร)
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
                # ควบคุมงูตัวที่ 2 (W, A, S, D)
                if event.key == pygame.K_a and self.direction2 != Direction.RIGHT:
                    self.direction2 = Direction.LEFT
                elif event.key == pygame.K_d and self.direction2 != Direction.LEFT:
                    self.direction2 = Direction.RIGHT
                elif event.key == pygame.K_w and self.direction2 != Direction.DOWN:
                    self.direction2 = Direction.UP
                elif event.key == pygame.K_s and self.direction2 != Direction.UP:
                    self.direction2 = Direction.DOWN

        # 2. เคลื่อนที่งูทั้งสอง
        self._move(self.direction, self.snake)
        self._move(self.direction2, self.snake2)

        # 3. ตรวจสอบว่าจบเกมหรือไม่
        game_over = False
        if self.is_collision(self.snake) or self.is_collision(self.snake2):
            game_over = True
            return game_over, self.score, self.score2  # ส่งกลับคะแนนทั้งสอง

        # 4. วางอาหารใหม่หรือเคลื่อนที่ต่อไป
        if self.snake[0] == self.food:
            self.score += 1  # เพิ่มคะแนนของงูตัวที่ 1
            self._place_food()
        else:
            self.snake.pop()

        if self.snake2[0] == self.food:
            self.score2 += 1  # เพิ่มคะแนนของงูตัวที่ 2
            self._place_food()
        else:
            self.snake2.pop()

        # 5. ตรวจสอบเวลา
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= self.time_limit:
            game_over = True
            return game_over, self.score, self.score2

        # 6. อัปเดต UI และเวลา
        self._update_ui()
        self.clock.tick(SPEED)

        # 7. ส่งกลับสถานะเกมและคะแนนทั้งสอง
        return game_over, self.score, self.score2

    def is_collision(self, snake):
        head = snake[0]
        # ชนขอบจอ
        if head.x >= self.w or head.x < 0 or head.y >= self.h or head.y < 0:
            return True
        # ชนตัวเองหรืองูอีกตัว
        if head in snake[1:] or head in self.snake2[1:] or head in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        self.display.fill(BLACK)
        # ว่างูตัวที่ 1
        for pt in self.snake:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREEN2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        # ว่างูตัวที่ 2
        for pt in self.snake2:
            pygame.draw.rect(self.display, YELLOW, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, YELLOW2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))
        # ว่างอาหาร
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        # แสดงคะแนนของงูตัวที่ 1 และ 2
        text = font.render("1: " + str(self.score), True, WHITE)
        text2 = font.render(" 2: " + str(self.score2), True, WHITE)
        self.display.blit(text, [0, 0])
        self.display.blit(text2, [0, 30])
        # แสดงเวลาที่เหลือ
        elapsed_time = int(time.time() - self.start_time)
        remaining_time = max(0, self.time_limit - elapsed_time)
        time_text = font.render("Time: " + str(remaining_time), True, WHITE)
        self.display.blit(time_text, [0, 60])
        pygame.display.flip()

    def _move(self, direction, snake):
        x = snake[0].x
        y = snake[0].y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        snake.insert(0, Point(x, y))

# Function to ask the player if they want to play again
def ask_play_again():
    popup = tk.Toplevel()
    popup.title("เล่นอีกครั้ง?")
    popup.geometry("300x150")

    # Message
    label = tk.Label(popup, text="Do you want to play again?", font=("Arial", 14))
    label.pack(pady=20)

    # Variable to store the result
    result = tk.BooleanVar()

    # "ใช่" button
    yes_button = tk.Button(popup, text="Yes", command=lambda: [result.set(True), popup.destroy()], width=10)
    yes_button.pack(side=tk.LEFT, padx=20)

    # "ไม่" button
    no_button = tk.Button(popup, text="No", command=lambda: [result.set(False), popup.destroy()], width=10)
    no_button.pack(side=tk.RIGHT, padx=20)

    # Wait until the user presses a button
    popup.wait_window()

    return result.get()

# Function to start the 2-player Snake game
def start_game():
    root.withdraw()  # Hide the UI window
    time_limit = simpledialog.askinteger("Time Limit", "Enter the time limit in seconds:", parent=root, minvalue=1, maxvalue=600)
    if time_limit is None:
        time_limit = 60  # Default time limit if user cancels
    game = SnakeGame(time_limit=time_limit)
    while True:
        game_over, score1, score2 = game.play_step()
        if game_over:
            winner = "Player 1" if score1 > score2 else "Player 2" if score2 > score1 else "It's a tie!"
            messagebox.showinfo("Game Over", f"Time's up! {winner} wins!\nPlayer 1 Score: {score1}, Player 2 Score: {score2}")
            play_again = ask_play_again()
            if not play_again:
                pygame.quit()  # Close PyGame
                root.deiconify()  # Show the UI window again
                break  # Exit the game loop
            else:
                game.reset()  # Reset the game

# Function to run the test_model.py file
def run_test_model():
    root.withdraw()  # Hide the UI window
    subprocess.run(["python", "test_model.py"])  # Run the test_model.py file
    root.deiconify()  # Show the UI window again

# Create the UI window
root = tk.Tk()
root.title("Snake Game Menu")
root.geometry("300x200")

# Start Game Button
start_button = tk.Button(root, text="Start 2 Players", command=start_game, width=20, height=2)
start_button.pack(pady=10)

# Run Test Model Button
test_model_button = tk.Button(root, text="Go Play with AI", command=run_test_model, width=20, height=2)
test_model_button.pack(pady=10)

# Quit Game Button
quit_button = tk.Button(root, text="Quit Game", command=root.destroy, width=20, height=2)
quit_button.pack(pady=10)

# Start the UI
root.mainloop()
