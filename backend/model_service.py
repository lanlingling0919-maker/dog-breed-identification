import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os

# 【修改】使用绝对路径动态获取 models 文件夹下的模型文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 路径指向上一层目录的 models 文件夹
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "best_dog_model.pth")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ====================
# 加载模型
# ====================
# 检查模型是否存在
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"找不到模型文件：{MODEL_PATH}，请确认文件已放入 models 文件夹。")

checkpoint = torch.load(MODEL_PATH, map_location=device)
classes = checkpoint["classes"]

model = models.resnet50(weights=None)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, len(classes))

model.load_state_dict(checkpoint["model_state_dict"])
model.to(device)
model.eval()

print(f"✅ 模型加载成功，模型位置：{MODEL_PATH}")

# 图像预处理
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406], [0.229,0.224,0.225])
])

def predict_dog(image):
    image_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(image_tensor)
        probs = torch.softmax(outputs, dim=1)
        confidence, pred = torch.max(probs, 1)

    breed = classes[pred.item()]
    return {
        "breed": breed,
        "confidence": confidence.item()
    }