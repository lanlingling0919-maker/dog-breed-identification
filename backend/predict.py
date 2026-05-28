import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os

class DogPredictor:
    def __init__(self, model_path='best_dog_model.pth'):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 1. 重新构建模型结构
        self.model = models.resnet50(weights=None)
        num_ftrs = self.model.fc.in_features
        
        # 2. 加载权重
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        self.classes = checkpoint['classes'] # 取出训练时保存的类别名
        self.model.fc = nn.Linear(num_ftrs, len(self.classes))
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()

        # 3. 定义预处理（必须与验证集完全一致）
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, image_pil):
        # 预处理图片
        img_tensor = self.transform(image_pil).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(img_tensor)
            prob = torch.nn.functional.softmax(outputs, dim=1)
            conf, predicted = torch.max(prob, 1)
            
        return self.classes[predicted.item()], conf.item()

# 测试代码
if __name__ == "__main__":

    # 测试图片文件夹
    test_folder = "test_images"

    # 检查文件夹是否存在
    if not os.path.exists(test_folder):
        print(f"❌ 找不到文件夹：{test_folder}")
        exit()

    # 创建预测器
    predictor = DogPredictor(
        'best_dog_model.pth'
    )

    # 支持的图片格式
    image_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp"
    )

    # 获取所有图片
    image_files = [

        file for file
        in os.listdir(test_folder)

        if file.lower().endswith(
            image_extensions
        )
    ]

    if len(image_files) == 0:
        print("❌ 文件夹内没有图片")
        exit()

    print(
        f"\n开始测试 "
        f"{len(image_files)} 张图片...\n"
    )

    # 批量预测
    for image_name in image_files:

        image_path = os.path.join(
            test_folder,
            image_name
        )

        try:
            img = Image.open(
                image_path
            ).convert('RGB')

            breed, confidence = (
                predictor.predict(img)
            )

            print(
                f"{image_name}"
                f" → "
                f"{breed}"
                f" "
                f"({confidence*100:.2f}%)"
            )

        except Exception as e:

            print(
                f"{image_name}"
                f" 测试失败："
                f"{str(e)}"
            )

    print("\n✅ 批量测试完成")