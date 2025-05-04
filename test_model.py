import torch
import numpy as np
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet
import time
import tkinter as tk
from tkinter import messagebox
import pygame
import subprocess  # นำเข้าโมดูล subprocess เพื่อเรียกใช้ไฟล์ภายนอก

# ฟังก์ชันสำหรับรับสถานะของเกม
def get_state(game):
    head = game.snake[0]  # หัวของงู (AI)
    point_l = Point(head.x - 20, head.y)  # จุดทางซ้ายของหัวงู
    point_r = Point(head.x + 20, head.y)  # จุดทางขวาของหัวงู
    point_u = Point(head.x, head.y - 20)  # จุดทางบนของหัวงู
    point_d = Point(head.x, head.y + 20)  # จุดทางล่างของหัวงู

    dir_l = game.direction == Direction.LEFT  # งูเคลื่อนที่ไปทางซ้าย
    dir_r = game.direction == Direction.RIGHT  # งูเคลื่อนที่ไปทางขวา
    dir_u = game.direction == Direction.UP  # งูเคลื่อนที่ไปทางบน
    dir_d = game.direction == Direction.DOWN  # งูเคลื่อนที่ไปทางล่าง

    state = [
        # อันตรายข้างหน้า
        (dir_r and game.is_collision(point_r)) or
        (dir_l and game.is_collision(point_l)) or
        (dir_u and game.is_collision(point_u)) or
        (dir_d and game.is_collision(point_d)),

        # อันตรายทางขวา
        (dir_u and game.is_collision(point_r)) or
        (dir_d and game.is_collision(point_l)) or
        (dir_l and game.is_collision(point_u)) or
        (dir_r and game.is_collision(point_d)),

        # อันตรายทางซ้าย
        (dir_d and game.is_collision(point_r)) or
        (dir_u and game.is_collision(point_l)) or
        (dir_r and game.is_collision(point_u)) or
        (dir_l and game.is_collision(point_d)),

        # ทิศทางการเคลื่อนที่
        dir_l,
        dir_r,
        dir_u,
        dir_d,

        # ตำแหน่งของอาหาร
        game.food.x < game.head.x,  # อาหารอยู่ทางซ้าย
        game.food.x > game.head.x,  # อาหารอยู่ทางขวา
        game.food.y < game.head.y,  # อาหารอยู���ทางบน
        game.food.y > game.head.y  # อาหารอยู่ทางล่าง
    ]

    return np.array(state, dtype=int)

# โหลดโมเดลที่บันทึกไว้
model = Linear_QNet(11, 512, 3)
model.load('best_model.pth')
model.eval()  # ตั้งค่าโมเดลให้อยู่ในโหมดประเมินผล

# ฟังก์ชันสำหรับถามผู้เล่นว่าต้องการเล่นอีกครั้งหรือไม่
def ask_play_again():
    popup = tk.Toplevel()
    popup.title("เล่นอีกครั้ง?")
    popup.geometry("300x150")

    # ข้อความ
    label = tk.Label(popup, text="ต้องการเล่นอีกครั้งไหม?", font=("Arial", 14))
    label.pack(pady=20)

    # ตัวแปรสำหรับเก็บผลลัพธ์
    result = tk.BooleanVar()

    # ปุ่ม "ใช่"
    yes_button = tk.Button(popup, text="ใช่", command=lambda: [result.set(True), popup.destroy()], width=10)
    yes_button.pack(side=tk.LEFT, padx=20)

    # ปุ่ม "ไม่"
    no_button = tk.Button(popup, text="ไม่", command=lambda: [result.set(False), popup.destroy()], width=10)
    no_button.pack(side=tk.RIGHT, padx=20)

    # รอจนกว่าผู้เล่นจะกดปุ่ม
    popup.wait_window()

    return result.get()

# ฟังก์ชันสำหรับเริ่มเกม
def start_game():
    root.withdraw()  # ซ่อนหน้าต่าง UI

    # เริ่มต้นเกม
    game = SnakeGameAI()

    while True:
        # เล่นเกมจนจบ
        while True:
            state = get_state(game)

            # แปลงสถานะเป็นเทนเซอร์และคำนวณการเคลื่อนที่
            state_tensor = torch.tensor(state, dtype=torch.float)
            prediction = model(state_tensor)
            move = torch.argmax(prediction).item()  # คำนวณการเคลื่อนที่

            final_move = [0, 0, 0]
            final_move[move] = 1

            # เล่นเกมหนึ่งขั้นตอน
            reward, done, score, score2, winner = game.play_step(final_move)

            # หากเกมจบ
            if done:
                print(f"คะแนน 1 (AI): {score}, คะแนน 2 (ผู้เล่น): {score2}")
                print(f"เกมจบ! {winner}")
                game.reset()  # รีเซ็ตเกม
                break  # ออกจากลูปเกม

        # ถามผู้เล่นว่าต้องการเล่นอีกครั้งหรือไม่
        play_again = ask_play_again()
        if not play_again:
            # ถามผู้เล่นว่าต้องการออกจากเกมหรือไม่
            quit_game = messagebox.askyesno("ออกจากเกม?", "ต้องการออกจากเกมไหม?")
            if quit_game:
                pygame.quit()  # ปิด PyGame
                break  # ออกจากลูปเกม
            else:
                # ปิดหน้าต่างเกมและกลับไปที่เมนู
                pygame.quit()  # ปิด PyGame
                root.deiconify()  # แสดงหน้าต่าง UI อีกครั้ง
                break  # ออกจากลูปเกม

# ฟังก์ชันสำหรับจัดการปุ่ม "โหมดผู้เล่น 2 คน"
def go_to_2player_mode():
    root.destroy()  # ปิดหน้าต่างปัจจุบัน
    subprocess.run(["python", "2playermode.py"])  # เรียกใช้ไฟล์ 2playermode.py

# สร้างหน้าต่าง UI

root = tk.Tk()
root.title("เมนูเกมงู")
root.geometry("300x200")

# ปุ่มเริ่มเกม
start_button = tk.Button(root, text="เริ่มเล่นกับ AI", command=start_game, width=20, height=2)
start_button.pack(pady=10)

# ปุ่มโหมดผู้เล่น 2 คน
player2_button = tk.Button(root, text="โหมดผู้เล่น 2 คน", command=go_to_2player_mode, width=20, height=2)
player2_button.pack(pady=10)

# ปุ่มออกจากเกม
quit_button = tk.Button(root, text="ออกจากเกม", command=root.destroy, width=20, height=2)
quit_button.pack(pady=10)

# เริ่มต้น UI
root.mainloop()
