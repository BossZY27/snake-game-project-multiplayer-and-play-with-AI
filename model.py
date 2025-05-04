import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os


class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        # กำหนดโครงสร้างของ Neural Network
        self.linear1 = nn.Linear(input_size, hidden_size)  # Layer แรก
        self.linear2 = nn.Linear(hidden_size, output_size)  # Layer ที่สอง
        self.best_score = float('-inf')  # เก็บคะแนนที่ดีที่สุด

    def forward(self, x):
        # การคำนวณ Forward Pass
        x = F.relu(self.linear1(x))  # ใช้ ReLU เป็น Activation Function
        x = self.linear2(x)  # Layer ที่สอง
        return x

    def save(self, score, file_name='best_model.pth'):
        # บันทึกโมเดลถ้าคะแนนดีกว่าคะแนนที่ดีที่สุด
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)  # สร้างโฟลเดอร์ถ้ายังไม่มี

        file_name = os.path.join(model_folder_path, file_name)

        # บันทึกถ้าคะแนนดีกว่าคะแนนที่ดีที่สุด
        if score > self.best_score:
            self.best_score = score  # อัปเดตคะแนนที่ดีที่สุด
            torch.save({'model_state_dict': self.state_dict(), 'best_score': self.best_score}, file_name)
            print(f"✅ Model saved with new best score: {score}")

    def load(self, file_name='best_model.pth', train_mode=True):
        # โหลดโมเดลที่บันทึกไว้
        model_folder_path = './model'
        file_name = os.path.join(model_folder_path, file_name)
        if os.path.exists(file_name):
            checkpoint = torch.load(file_name)
            self.load_state_dict(checkpoint['model_state_dict'])  # โหลด weights
            self.best_score = checkpoint.get('best_score', float('-inf'))  # โหลดคะแนนที่ดีที่สุด

            if train_mode:
                self.train()  # กลับไปโหมด Train
            else:
                self.eval()  # ใช้สำหรับ Predict เท่านั้น

            print(f"✅ Model loaded from {file_name} with best score: {self.best_score}")
        else:
            print(f"⚠️ File {file_name} not found!")


class QTrainer:
    def __init__(self, model, lr, gamma):
        # กำหนดค่าเริ่มต้นสำหรับ Trainer
        self.lr = lr  # Learning Rate
        self.gamma = gamma  # Discount Factor
        self.model = model  # โมเดลที่ใช้ฝึก
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)  # ใช้ Adam Optimizer
        self.criterion = nn.MSELoss()  # ใช้ Mean Squared Error เป็น Loss Function

    def train_step(self, state, action, reward, next_state, done):
        # ฝึกโมเดลด้วยข้อมูลที่ให้มา
        state = torch.tensor(state, dtype=torch.float)  # แปลง state เป็น tensor
        next_state = torch.tensor(next_state, dtype=torch.float)  # แปลง next_state เป็น tensor
        action = torch.tensor(action, dtype=torch.long)  # แปลง action เป็น tensor
        reward = torch.tensor(reward, dtype=torch.float)  # แปลง reward เป็น tensor
        done = torch.tensor(done, dtype=torch.bool)  # แปลง done เป็น tensor

        # ปรับรูปร่างของ tensor ถ้าข้อมูลมีมิติเดียว
        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = torch.unsqueeze(done, 0)

        pred = self.model(state)  # ค่าคาดการณ์จากโมเดล
        target = pred.clone()  # คัดลอกค่าคาดการณ์เพื่อใช้เป็น target

        with torch.no_grad():  # ป้องกันการคำนวณ gradient ซ้ำซ้อน
            next_pred = self.model(next_state)  # ค่าคาดการณ์สำหรับ state ถัดไป
            max_next_Q = torch.max(next_pred, dim=1)[0]  # ค่า Q สูงสุด
            target_Q = reward + (self.gamma * max_next_Q * ~done)  # คำนวณค่า Q เป้าหมาย

        # อัปเดตค่าตาม action ที่เลือกไว้
        target[range(len(action)), action.argmax(dim=1)] = target_Q

        self.optimizer.zero_grad()  # ล้าง gradient ก่อนคำนวณใหม่
        loss = self.criterion(target, pred)  # คำนวณ loss
        loss.backward()  # Backpropagation
        self.optimizer.step()  # อัปเดต weights
