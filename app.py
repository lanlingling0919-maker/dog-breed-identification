from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import os

# 【修改】从 backend 文件夹导入
from backend.model_service import predict_dog

# 【修改】由于 app.py 在根目录，直接使用默认配置即可
app = Flask(__name__)
            
app.config['JSON_AS_ASCII'] = False

# 允许前端跨域访问
CORS(app)

# ==========================
# 狗品种中英文映射 (保持不变)
# ==========================
DOG_BREEDS_DICT = {
    "boston_bull": "波士顿梗", "dingo": "澳洲野犬", "pekinese": "京巴犬",
    "bluetick": "布鲁塞尔格里芬犬", "golden_retriever": "金毛寻回犬",
    "bedlington_terrier": "贝灵顿梗", "borzoi": "俄罗斯猎狼犬",
    "basenji": "巴森吉犬", "scottish_deerhound": "苏格兰猎鹿犬",
    "shetland_sheepdog": "喜乐蒂牧羊犬", "walker_hound": "波兰猎犬",
    "maltese_dog": "马尔济斯犬", "norfolk_terrier": "诺福克梗",
    "african_hunting_dog": "非洲野犬", "wire-haired_fox_terrier": "刚毛猎狐梗",
    "redbone": "红骨猎浣熊犬", "lakeland_terrier": "湖畔梗",
    "boxer": "拳师犬", "doberman": "杜宾犬", "otterhound": "奥达猎犬",
    "standard_schnauzer": "标准雪纳瑞", "irish_water_spaniel": "爱尔兰水猎犬",
    "black-and-tan_coonhound": "黑褐猎浣熊犬", "cairn": "凯恩梗",
    "affenpinscher": "艾芬品", "labrador_retriever": "拉布拉多犬",
    "ibizan_hound": "伊比赞猎犬", "english_setter": "英国塞特犬",
    "weimaraner": "威玛猎犬", "giant_schnauzer": "巨型雪纳瑞",
    "groenendael": "比利时牧羊犬", "dhole": "亚洲豺犬",
    "toy_poodle": "玩具贵宾犬", "border_terrier": "边境梗",
    "tibetan_terrier": "西藏梗", "norwegian_elkhound": "挪威猎鹿犬",
    "shih-tzu": "西施犬", "irish_terrier": "爱尔兰梗",
    "kuvasz": "库瓦兹犬", "german_shepherd": "德国牧羊犬",
    "greater_swiss_mountain_dog": "大瑞士山地犬", "basset": "巴吉度猎犬",
    "australian_terrier": "澳洲梗", "schipperke": "舒伯齐犬",
    "rhodesian_ridgeback": "罗德西亚背脊犬", "irish_setter": "爱尔兰塞特犬",
    "appenzeller": "阿彭策尔山地犬", "bloodhound": "寻血猎犬",
    "samoyed": "萨摩耶犬", "miniature_schnauzer": "迷你雪纳瑞",
    "brittany_spaniel": "布列塔尼猎犬", "kelpie": "卡尔比犬",
    "papillon": "蝴蝶犬", "border_collie": "边境牧羊犬",
    "entlebucher": "恩特雷布赫山地犬", "collie": "柯利牧羊犬",
    "malamute": "阿拉斯加雪橇犬", "welsh_springer_spaniel": "威尔士史宾格犬",
    "chihuahua": "吉娃娃", "saluki": "萨路基猎犬",
    "pug": "八哥犬", "malinois": "马里努阿犬",
    "komondor": "可蒙犬", "airedale": "万能梗",
    "leonberg": "兰伯格犬", "mexican_hairless": "墨西哥无毛犬",
    "bull_mastiff": "斗牛獒", "bernese_mountain_dog": "伯恩山犬",
    "american_staffordshire_terrier": "美系斯塔福梗", "lhasa": "拉萨犬",
    "cardigan": "卡迪根柯基", "italian_greyhound": "意大利灵缇",
    "clumber": "克伦伯猎犬", "scotch_terrier": "苏格兰梗",
    "afghan_hound": "阿富汗猎犬", "old_english_sheepdog": "古英国牧羊犬",
    "saint_bernard": "圣伯纳犬", "miniature_pinscher": "迷你杜宾",
    "eskimo_dog": "爱斯基摩犬", "irish_wolfhound": "爱尔兰猎狼犬",
    "brabancon_griffon": "布鲁塞尔格里芬", "toy_terrier": "玩具梗",
    "chow": "松狮犬", "flat-coated_retriever": "平毛寻回犬",
    "norwich_terrier": "诺威奇梗", "soft-coated_wheaten_terrier": "软毛小麦梗",
    "staffordshire_bullterrier": "斯塔福斗牛梗", "english_foxhound": "英国猎狐犬",
    "gordon_setter": "戈登塞特犬", "siberian_husky": "哈士奇",
    "pembroke": "彭布罗克柯基", "pomeranian": "博美犬",
    "beagle": "比格犬", "vizsla": "维兹拉犬",
    "kerry_blue_terrier": "凯利蓝梗", "whippet": "惠比特犬",
    "dandie_dinmont": "丹第丁蒙梗", "sealyham_terrier": "西里汉梗",
    "standard_poodle": "标准贵宾犬", "keeshond": "荷兰毛狮犬",
    "japanese_spaniel": "日本狆", "miniature_poodle": "迷你贵宾犬",
    "curly-coated_retriever": "卷毛寻回犬", "yorkshire_terrier": "约克夏梗",
    "silky_terrier": "丝毛梗", "sussex_spaniel": "萨塞克斯猎犬",
    "french_bulldog": "法国斗牛犬", "bouvier_des_flandres": "法兰德斯牧牛犬",
    "tibetan_mastiff": "藏獒", "cocker_spaniel": "可卡犬",
    "great_dane": "大丹犬", "blenheim_spaniel": "查理王小猎犬",
    "rottweiler": "罗威纳犬", "german_short-haired_pointer": "德国短毛指示犬",
    "english_springer": "英国史宾格犬", "newfoundland": "纽芬兰犬"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "message": "后端运行正常"})

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '未检测到上传图片'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '未选择图片'}), 400

    try:
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # 调用模型预测
        result = predict_dog(image)
        breed_en = result["breed"]
        confidence = result["confidence"]
        
        breed_cn = DOG_BREEDS_DICT.get(breed_en, "未知品种")

        response = {
            "success": True,
            "breed_en": breed_en,
            "breed_cn": breed_cn,
            "confidence": round(confidence, 4),
            "confidence_pct": f"{confidence * 100:.2f}%",
            "message": f"识别成功！该狗品种可能是：{breed_cn}"
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)