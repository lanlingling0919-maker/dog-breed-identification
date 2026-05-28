import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import os

def get_data_loaders(data_dir='dataset_final', batch_size=32, image_size=224):
    """
    配置数据增强并返回训练/验证加载器
    :param data_dir: 数据集根目录
    :param batch_size: 批处理大小
    :param image_size: 输入模型的图像尺寸（通常CNN为224或299）
    """
    
    # 1. 定义【训练集】的增强方案：旨在让模型见过各种各样的“变种”狗
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(image_size), # 随机裁剪并缩放
        transforms.RandomHorizontalFlip(),       # 随机水平翻转（狗头向左或向右不影响品种）
        transforms.RandomRotation(15),           # 随机旋转一个小角度
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2), # 随机亮度/对比度
        transforms.ToTensor(),                   # 转为张量
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]) # ImageNet 标准标准化
    ])

    # 2. 定义【验证集】的方案：不加随机干扰，只做必要的标准化
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 3. 加载数据集 (利用你之前整理好的子文件夹结构)
    train_path = os.path.join(data_dir, 'train')
    val_path = os.path.join(data_dir, 'val')

    train_dataset = datasets.ImageFolder(train_path, transform=train_transform)
    val_dataset = datasets.ImageFolder(val_path, transform=val_transform)

    # 4. 创建 DataLoader
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4)

    print(f"✅ 数据加载成功！共识别出 {len(train_dataset.classes)} 个品种。")
    print(f"训练样本数: {len(train_dataset)}, 验证样本数: {len(val_dataset)}")
    
    return train_loader, val_loader, train_dataset.classes

# 快速测试脚本 (在 VS Code 直接运行 loader.py 时触发)
if __name__ == "__main__":
    tl, vl, classes = get_data_loaders()
    # 打印前5个品种确认一下
    print("前5个品种名:", classes[:5])