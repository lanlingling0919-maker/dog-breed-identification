document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const predictBtn = document.getElementById('predict-btn');
    const preview = document.getElementById('image-preview');
    const previewContainer = document.getElementById('preview-container');
    const resultArea = document.getElementById('result-area');
    const loader = document.getElementById('loader');

    // 1. 图片预览逻辑 (刘童要求的功能)
    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                previewContainer.style.display = 'block';
                predictBtn.disabled = false;
                resultArea.style.display = 'none';
            };
            reader.readAsDataURL(file);
        }
    });

    // 2. 异步 API 调用逻辑 (你的核心任务)
    predictBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        // 显示加载状态
        loader.style.display = 'block';
        predictBtn.disabled = true;
        resultArea.style.display = 'none';

        try {
            // 发送 POST 请求到 Flask 接口
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // 3. 将后端返回的 JSON 渲染到页面上
                document.getElementById('res-cn').innerText = data.breed_cn;
                document.getElementById('res-en').innerText = data.breed_en;
                document.getElementById('res-conf').innerText = data.confidence_pct;
                
                resultArea.style.display = 'block';
            } else {
                alert("识别失败：" + data.error);
            }
        } catch (error) {
            console.error("Error:", error);
            alert("服务器连接失败");
        } finally {
            loader.style.display = 'none';
            predictBtn.disabled = false;
        }
    });
});