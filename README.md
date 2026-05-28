# 🐕 AI 智能犬种识别系统 (Dog Breed Identification)

本项目是《工程实践四（人工智能应用开发）》的课程作业。系统基于 **Flask + PyTorch (ResNet50)** 架构，实现了对 120 种常见狗品种的自动化识别，并提供了标准的前后端分离 Web 交互界面。

---

## 👨‍💻 小组成员与分工

| 成员 | 角色 | 具体职责 |
| :--- | :--- | :--- |
| **兰棱棱 (组长)** | **项目经理 / 优化辅助** | 负责项目整体规划、目录结构整理、模型训练辅助及项目文档编写。 |
| **周洲** | **算法开发工程师** | 负责 CNN 模型（ResNet50）的搭建、超参数调优及模型训练。 |
| **刘童** | **前端 UI 工程师** | 负责 Web 界面 UI 设计、HTML 骨架搭建、CSS 视觉美化及响应式适配。 |
| **郑柯月** | **后端逻辑/联调工程师** | 负责 Flask 服务器搭建、RESTful API 开发及前后端数据通信联调。 |

---

## 🚀 启动指南 (快速开始)

请按照以下步骤配置环境并启动系统：

### 1. 创建虚拟环境 (Anaconda)
打开终端或 Anaconda Prompt，输入以下命令创建并激活环境：
```bash
# 创建 Python 3.10 环境
conda create -n dog_ai python=3.10 -y

# 激活环境
conda activate dog_ai
```

### 2. 安装项目依赖
在项目根目录下，使用 `pip` 安装必要的库：
```bash
pip install flask flask-cors pillow torch torchvision
```
*(注：若需 GPU 加速，请根据官网指令安装对应的 CUDA 版本)*

### 3. 模型权重准备 (关键步骤)
由于 GitHub 文件大小限制，模型权重文件并未上传至仓库。
- **操作：** 请在根目录下手动创建 `models/` 文件夹。
- **放置：** 将训练好的模型文件 `best_dog_model.pth` 放入 `models/` 文件夹中。

### 4. 启动后端服务
在根目录下运行启动脚本：
```bash
python app.py
```
当看到 `✅ 模型加载成功` 且提示 `Running on http://127.0.0.1:5000` 时，表示服务启动成功。

### 5. 访问系统
打开浏览器（推荐 Chrome 或 Edge），访问以下地址：
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📂 项目目录结构
```text
dog-breed-identification/
├── app.py                 # Flask 服务器主程序（入口）
├── requirements.txt       # 项目依赖清单
├── .gitignore             # 忽略大文件配置
├── README.md              # 本说明文档
├── backend/               # 后端核心逻辑
│   ├── __init__.py        # 包初始化文件
│   └── model_service.py   # 模型加载与推理服务
├── models/                # 存放模型权重（.pth文件）
├── static/                # 静态资源（CSS, JS, 图片）
│   ├── css/
│   └── js/
├── templates/             # HTML 模板
│   └── index.html
└── training/              # 模型训练相关脚本与数据
```

---

## 🛠️ 技术选型
- **算法层**：PyTorch + ResNet50 (迁移学习)
- **后端层**：Python + Flask (RESTful API)
- **前端层**：HTML5 + Bootstrap 5 + JavaScript (Fetch API 异步请求)
- **数据处理**：Pillow + Torchvision Transforms
```
