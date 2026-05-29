document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const predictBtn = document.getElementById('predict-btn');
    const preview = document.getElementById('image-preview');
    const previewContainer = document.getElementById('preview-container');
    const resultArea = document.getElementById('result-area');
    const loader = document.getElementById('loader');
    const confBar = document.getElementById('conf-bar');
    const placeholder = document.getElementById('placeholder-box');
    const defaultMsg = document.getElementById('default-msg');

    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                previewContainer.style.display = 'flex';
                placeholder.style.display = 'none';
                predictBtn.disabled = false;
                resultArea.style.display = 'none';
                defaultMsg.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });

    predictBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        loader.style.display = 'block';
        defaultMsg.style.display = 'none';
        predictBtn.disabled = true;
        resultArea.style.display = 'none';

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                document.getElementById('res-cn').innerText = data.breed_cn;
                document.getElementById('res-en').innerText = data.breed_en;
                document.getElementById('res-conf').innerText = data.confidence_pct;
                if(confBar) confBar.style.width = data.confidence_pct;
                resultArea.style.display = 'block';
            } else {
                alert("识别失败：" + data.error);
                defaultMsg.style.display = 'block';
            }
        } catch (error) {
            alert("后端连接失败");
            defaultMsg.style.display = 'block';
        } finally {
            loader.style.display = 'none';
            predictBtn.disabled = false;
        }
    });
});