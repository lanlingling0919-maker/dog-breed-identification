# 🐕 AI 智能犬种识别系统 (Dog Breed Identification)

本项目是《工程实践四（人工智能应用开发）》的课程作业。通过深度学习技术，实现对 120 种常见狗品种的自动识别，并提供美观的 Web 交互界面。

## 🌟 项目亮点
- **标准 Web 架构**：采用 Flask (后端) + HTML5/CSS3/JS (前端) 的前后端分离架构。
- **高性能模型**：基于卷积神经网络（ResNet50）进行迁移学习，具备较高的识别准确率。
- **异步交互**：使用 Fetch API 实现图片的无刷新异步上传与识别结果回显。
- **响应式设计**：基于 Bootstrap 5 构建，适配 PC 与移动端浏览器。

## 👨‍💻 小组成员与分工
| 成员 | 角色 | 具体职责 |
| :--- | :--- | :--- |
| **兰棱棱 (组长)** | **项目经理 / 优化辅助** | 负责项目整体规划、目录结构整理、模型训练辅助及项目文档编写。 |
| **周洲** | **算法开发工程师** | 负责 CNN 模型（ResNet50）的搭建、超参数调优及模型训练。 |
| **刘童** | **前端 UI 工程师** | 负责 Web 界面 UI 设计、HTML 骨架搭建、CSS 视觉美化及响应式适配。 |
| **郑柯月** | **后端逻辑/联调工程师** | 负责 Flask 服务器搭建、RESTful API 开发及前后端数据通信联调。 |

## 🛠️ 技术栈
- **核心算法**：Python, PyTorch, Torchvision (ResNet50)
- **后端服务**：Flask, Flask-CORS
- **前端技术**：HTML5, CSS3, JavaScript, Bootstrap 5
- **图像处理**：Pillow (PIL)

## 📂 项目目录结构
```text
dog-breed-identification/
├── app.py                 # Flask 服务器启动入口
├── requirements.txt       # 项目依赖包清单
├── .gitignore             # Git 忽略文件配置
├── README.md              # 项目说明文档
├── backend/               # 后端核心逻辑文件夹
│   ├── __init__.py        # 包初始化文件
│   └── model_service.py   # 模型加载与推理服务
├── models/                # 模型权重存放目录（本地存放）
│   └── best_dog_model.pth
├── static/                # 静态资源（CSS, JS, 图片）


│   ├── css/
│   └── js/
└── templates/             # HTML 模板页面
    └── index.html
## 🚀 快速启动指南
1. 环境准备
建议使用 Anaconda 创建虚拟环境：
code
Bash
conda create -n dog_ai python=3.10
conda activate dog_ai
2. 安装依赖
code
Bash
pip install -r requirements.txt
3. 运行项目
在项目根目录下执行：
code
Bash
python app.py
启动后，在浏览器访问：http://127.0.0.1:5000
📊 实验结果
基础模型：ResNet50
识别种类：120 种
训练表现：见项目内 training/accuracy_plot.png
