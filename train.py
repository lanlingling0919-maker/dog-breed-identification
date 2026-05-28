import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from loader import get_data_loaders
from tqdm import tqdm
import os
import matplotlib.pyplot as plt  # 新增：用于绘图

def train_model():
    # 1. 硬件配置
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 2. 参数设置
    batch_size = 64
    epochs = 20
    learning_rate = 0.0003
    best_acc = 0.0

    # 新增：用于记录绘图数据的列表
    train_acc_history = []
    val_acc_history = []

    # 3. 获取数据加载器
    print("正在初始化数据流水线...")
    train_loader, val_loader, classes = get_data_loaders(batch_size=batch_size)

    # 4. 初始化模型
    print("正在加载本地预训练模型 ResNet50...")
    model = models.resnet50(weights=None) 
    local_weights_path = 'resnet50-11ad3fa6.pth'
    
    if os.path.exists(local_weights_path):
        state_dict = torch.load(local_weights_path)
        model.load_state_dict(state_dict)
        print("✅ 本地权重加载成功！")
    else:
        print(f"❌ 找不到权重文件 {local_weights_path}")
        return

    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, len(classes)) 
    model = model.to(device)

    # 5. 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    # 6. 正式训练循环
    print(f"\n🚀 训练启动！目标：识别 {len(classes)} 种狗狗")

    for epoch in range(epochs):
        # --- 训练阶段 ---
        model.train()
        running_loss = 0.0
        correct_train = 0  # 新增：记录训练集预测正确的数量
        total_train = 0    # 新增：记录训练集总数
        
        train_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]")
        
        for inputs, labels in train_bar:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
            # 新增：计算训练准确率
            _, predicted = torch.max(outputs.data, 1)
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()
            
            train_bar.set_postfix(loss=f"{loss.item():.4f}")

        # 计算并保存本轮训练准确率
        epoch_train_acc = 100 * correct_train / total_train
        train_acc_history.append(epoch_train_acc)

        # --- 验证阶段 ---
        model.eval()
        correct_val = 0
        total_val = 0
        print(f"正在对 Epoch {epoch+1} 进行考试（验证集测试）...")
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total_val += labels.size(0)
                correct_val += (predicted == labels).sum().item()
        
        val_acc = 100 * correct_val / total_val
        val_acc_history.append(val_acc) # 保存本轮验证准确率
        
        avg_train_loss = running_loss / len(train_loader)
        print(f"--- 结果汇报 ---")
        print(f"训练损耗: {avg_train_loss:.4f} | 训练准确率: {epoch_train_acc:.2f}% | 验证准确率: {val_acc:.2f}%")
        
        scheduler.step()

        # 7. 保存最优模型
        if val_acc > best_acc:
            best_acc = val_acc
            save_path = 'best_dog_model.pth'
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'classes': classes
            }, save_path)
            print(f"🌟 发现更好的模型！已保存")
        print("-" * 30)

    # --- 新增：绘图部分 ---
    print("\n📊 正在生成准确率曲线图...")
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, epochs + 1), train_acc_history, label='Training Accuracy', marker='o')
    plt.plot(range(1, epochs + 1), val_acc_history, label='Validation Accuracy', marker='s')
    plt.title('Training and Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    plt.grid(True)
    
    # 保存图片到本地
    plt.savefig('accuracy_plot.png')
    print("✅ 准确率曲线已保存为 'accuracy_plot.png'")
    
    # 显示图片
    plt.show()

    print(f"\n✅ 训练全部结束！历史最高准确率: {best_acc:.2f}%")

if __name__ == "__main__":
    train_model()