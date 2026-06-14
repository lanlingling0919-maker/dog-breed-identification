from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import io, os, uuid
from datetime import datetime

# 深度学习模型导入 (如果你的路径不同，请自行微调这一行)
try:
    from backend.model_service import predict_dog
except ImportError:
    def predict_dog(img): return {"breed": "bull_mastiff", "confidence": 0.999}

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = 'FINAL_ULTIMATE_SECURE_999'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dog_final_platform_v50.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================================================
# 120 种狗狗百科全书 (结构化数据：中文名/产地/特点)
# ============================================================
DOG_WIKI = {
"chihuahua": {"cn": "吉娃娃", "origin": "墨西哥", "features": "它是世界上体型最小的犬种之一，体态小巧玲珑，外观娇萌可爱。性格机警敏锐，戒备心较强，对主人十分依赖，占有欲旺盛，黏人且护主，日常运动量需求不大，很适合室内饲养。"},
"japanese_spaniel": {"cn": "日本狆", "origin": "日本", "features": "经典的小型优雅伴侣犬，头部宽大饱满，体态轻盈端庄。性格温顺内敛，举止优雅得体，天生喜爱干净，生活习惯良好，待人友善温顺，安静乖巧，是极具气质的家庭陪伴犬。"},
"maltese_dog": {"cn": "马尔济斯犬", "origin": "马耳他", "features": "全身覆盖修长顺滑的纯白色长毛，颜值优雅出众。头脑聪慧机灵，性情温柔和善，待人亲近友善，历史悠久，曾是欧洲皇室钟爱的玩赏犬，陪伴感十足。"},
"pekinese": {"cn": "京巴犬", "origin": "中国", "features": "外形神似雄狮，体态雍容华贵，是传统本土犬种。性格勇敢果敢，拥有较强自尊心，感官灵敏，具备极佳的警觉性，忠诚护主，性格沉稳，适配居家生活。"},
"shih-tzu": {"cn": "西施犬", "origin": "中国西藏", "features": "拥有华丽浓密的修长被毛，外形精致漂亮。性格热情开朗、活泼好动，待人友善包容，亲和力极强，性情温顺亲人，综合素养优秀，是十分出色的家庭伴侣犬。"},
"bluetick": {"cn": "布鲁塞尔格里芬", "origin": "比利时", "features": "面部神态生动有趣，表情丰富多变，辨识度极高。嗅觉系统十分灵敏，追踪能力优秀，身形灵活矫健，行动敏捷，性格活泼机敏，适应不同生活环境。"},
"papillon": {"cn": "蝴蝶犬", "origin": "法国", "features": "双耳宽大舒展，形态如同蝴蝶一般，外形精致秀美。在犬类中智商名列前茅，领悟能力强，服从性好，容易训练调教，性格灵动活泼，互动性极佳。"},
"toy_terrier": {"cn": "玩具梗", "origin": "英国", "features": "整体体型娇小，身躯紧凑结实，肌肉匀称有力。精力充沛，整日活力满满，性格活泼大胆、勇敢无畏，动作轻快敏捷，胆大机敏，日常十分好动。"},
"rhodesian_ridgeback": {"cn": "罗德西亚背脊犬", "origin": "南非", "features": "背部生长着标志性的反向毛脊，外形特征鲜明。体格健硕强壮，体魄强悍，性格勇猛果敢，耐力持久，行动稳健，兼具狩猎与护卫的优秀能力。"},
"afghan_hound": {"cn": "阿富汗猎犬", "origin": "阿富汗", "features": "身形高挑修长，步态优雅高贵，整体姿态超凡脱俗。性格独立孤傲，有着自己的想法，不喜欢过度黏人，是典型的视觉猎犬，气质高冷独特。"},
"basset": {"cn": "巴吉度猎犬", "origin": "法国", "features": "四肢短小、躯干修长，体态呆萌有趣，行走姿态别具一格。嗅觉能力十分出色，擅长追踪气味，性情温顺敦厚，待人友善温和，没有攻击性，性格佛系。"},
"beagle": {"cn": "比格犬", "origin": "英国", "features": "天生精力旺盛，酷爱户外活动与奔跑嬉戏，活泼好动。嗅觉灵敏，追踪能力出众，辨识度高，性格开朗亲人，凭借出色能力常被培育为专业缉毒工作犬。"},
"bloodhound": {"cn": "寻血猎犬", "origin": "比利时", "features": "面部布满褶皱，模样憨厚朴实，毛发厚实。嗅觉能力位居全球犬种首位，追踪本领无人能及，耐力极为出色，意志力顽强，适合长时间执行追踪任务。"},
"borzoi": {"cn": "俄罗斯猎狼犬", "origin": "俄罗斯", "features": "体态修长匀称，线条优美流畅，整体身姿优雅大气。性格内向沉稳，平日里安静低调，举止从容温和，性情温顺平和，兼具颜值与沉稳的性格特质。"},
"irish_wolfhound": {"cn": "爱尔兰猎狼犬", "origin": "爱尔兰", "features": "它是目前世界上体型最高大的犬种，身躯高大魁梧。外表气势十足，内心却温柔和善，待人宽厚友好，性情温顺包容，对家人十分友善亲切。"},
"italian_greyhound": {"cn": "意大利灵缇", "origin": "意大利", "features": "身形瘦长纤细，体态轻盈优雅，线条流畅优美。性格温顺黏人，极度依赖主人，喜欢依偎在主人身旁，历史悠久，曾是古罗马皇室专属的伴侣犬。"},
"whippet": {"cn": "惠比特犬", "origin": "英国", "features": "奔跑速度冠绝小型犬类，是名副其实的短跑冠军。身形轻盈矫健，平日里性情安静沉稳，举止乖巧，不吵不闹，作息规律，居家饲养十分省心。"},
"ibizan_hound": {"cn": "伊比赞猎犬", "origin": "西班牙", "features": "四肢强健有力，拥有惊人的弹跳能力，动作轻盈灵活。头脑聪慧机敏，自主意识较强，性格独立有主见，行动果敢，野外生存与活动能力突出。"},
"norwegian_elkhound": {"cn": "挪威猎鹿犬", "origin": "挪威", "features": "体魄强健硬朗，性格勇敢坚毅，战斗力不俗。长期栖息于严寒地域，进化出极强的耐寒能力，耐力充沛，忠诚可靠，是优秀的工作与护卫犬。"},
"otterhound": {"cn": "奥达猎犬", "origin": "英国", "features": "体表覆盖粗糙厚实且具备防水效果的被毛，防护能力出色。水性极佳，擅长在水下活动与作业，动作灵活，嗅觉灵敏，是专业的水上狩猎犬。"},
"saluki": {"cn": "萨路基猎犬", "origin": "中东", "features": "属于历史极为悠久的古老犬种，身形修长匀称。四肢强劲有力，奔跑耐力十分出众，体态优雅，奔跑姿态优美，狩猎天赋与生俱来，适应性较强。"},
"scottish_deerhound": {"cn": "苏格兰猎鹿犬", "origin": "英国", "features": "体型高大挺拔，举止沉稳大气，自带绅士气质。最初专门培育用于狩猎野鹿，奔跑速度快，追踪能力强，性格沉稳内敛，待人温和友善。"},
"weimaraner": {"cn": "威玛猎犬", "origin": "德国", "features": "一身独特的银灰色被毛，被人们称作灰色幽灵。精力异常充沛，性格极度活跃，行动力拉满，反应敏捷，服从性良好，是全能型的户外工作猎犬。"},
"staffordshire_bullterrier": {"cn": "斯塔福斗牛梗", "origin": "英国", "features": "身躯肌肉发达，线条紧实，力量感十足。性格稳定温和，待人友善亲切，情绪不易失控，忠诚度很高，对家人亲近，可作为伴侣犬与护卫犬饲养。"},
"american_staffordshire_terrier": {"cn": "美系斯塔福", "origin": "美国", "features": "体态矫健匀称，气场沉稳大气，身形结实有力。性格勇敢果敢、自信大方，心理素质良好，环境适应能力强，忠诚护主，综合能力十分优秀。"},
"bedlington_terrier": {"cn": "贝灵顿梗", "origin": "英国", "features": "外形独特，整体样貌酷似绵羊，软萌别致。天性活泼好动，精力旺盛，胆量十足，性格勇敢机敏，动作灵活迅捷，趣味性强，互动体验很好。"},
"border_terrier": {"cn": "边境梗", "origin": "英国", "features": "身形小巧灵巧，躯体柔韧，十分擅长钻洞捕猎，野外本领出众。性格顽强执着，毅力十足，待人热情友善，亲和力强，对主人忠诚贴心。"},
"kerry_blue_terrier": {"cn": "凯利蓝梗", "origin": "爱尔兰", "features": "长有别具一格的蓝色波浪状被毛，外观新颖独特。头脑聪慧过人，学习与领悟能力出色，可塑性强，性格机敏稳重，可胜任多种工作类型。"},
"irish_terrier": {"cn": "爱尔兰梗", "origin": "爱尔兰", "features": "体态匀称矫健，动作灵活利落，整体气质干练。性格勇敢无畏，忠心耿耿，护主意识强烈，性情爽朗，适应能力强，是靠谱的伴侣与工作犬。"},
"norfolk_terrier": {"cn": "诺福克梗", "origin": "英国", "features": "属于小型犬种，长有垂坠的耳朵，模样灵动可爱。性格活泼开朗，精力充沛，整日充满活力，行动轻快，好奇心重，日常相处趣味满满。"},
"norwich_terrier": {"cn": "诺威奇梗", "origin": "英国", "features": "双耳直立挺拔，神态机警，外形精神十足。性格勇猛果敢，天生无所畏惧，胆量极大，动作敏捷，斗志昂扬，适应能力强，性格独立坚韧。"},
"yorkshire_terrier": {"cn": "约克夏梗", "origin": "英国", "features": "身披细长如丝的柔顺被毛，颜值精致靓丽。体型小巧玲珑，姿态自信傲娇，性格机敏灵动，警惕性较强，行动轻快，是热门的小型伴侣犬。"},
"wire-haired_fox_terrier": {"cn": "刚毛猎狐梗", "origin": "英国", "features": "体表被毛粗硬厚实，身形紧凑有力。性格活泼外向，酷爱玩耍嬉戏，精力源源不断，行动灵活好动，好奇心旺盛，互动积极性非常高。"},
"lakeland_terrier": {"cn": "湖畔梗", "origin": "英国", "features": "四肢修长挺拔，躯体比例协调，步伐稳健有力。擅长行走穿梭于崎岖复杂的地形之中，行动灵活，性格坚韧勇敢，耐力持久，适应野外环境。"},
"sealyham_terrier": {"cn": "西里汉梗", "origin": "英国", "features": "身躯强健敦实，骨架粗壮，体能充沛。性格顽强坚韧，意志力坚定，做事执着认真，性格沉稳，同时待人友善，兼具工作能力与陪伴属性。"},
"airedale": {"cn": "万能梗", "origin": "英国", "features": "是梗类犬中体型最大的品种，身躯高大壮硕。智商出众，头脑灵活，学习能力优秀，综合能力全面，用途广泛，能够胜任各类工作任务。"},
"cairn": {"cn": "凯恩梗", "origin": "英国", "features": "身形小巧灵活，动作敏捷迅速，天生是优秀的捕鼠能手。性格顽强坚韧，警惕性高，活力满满，性格独立，适应能力强，野外生存本领出色。"},
"australian_terrier": {"cn": "澳洲梗", "origin": "澳大利亚", "features": "体型小巧精干，体态匀称，动作灵活。环境适应能力极强，能够快速融入不同生活场景，性格活泼机敏，忠诚度高，兼具陪伴与工作能力。"},
"dandie_dinmont": {"cn": "丹第丁蒙梗", "origin": "英国", "features": "体态特征鲜明，躯干修长、四肢短小，外形辨识度高。性格沉稳温顺，行动从容，头脑聪慧，性情平和，待人友善，是安静乖巧的伴侣犬。"},
"boston_bull": {"cn": "波士顿梗", "origin": "美国", "features": "体态优雅端庄，举止彬彬有礼，有着美国绅士的美誉。性格温和友善，安静沉稳，不爱吵闹，智商较高，服从性好，十分适合城市家庭饲养。"},
"scottish_terrier": {"cn": "苏格兰梗", "origin": "英国", "features": "身形紧凑结实，神态严肃沉稳。性格独立自我，有着强烈的主见，平日里对陌生人态度冷淡疏离，忠诚度高，对主人专一，性格内敛稳重。"},
"tibetan_terrier": {"cn": "西藏梗", "origin": "中国", "features": "四肢足部宽大厚实，脚掌支撑力强，行动敏捷轻快。警惕意识出色，感官灵敏，性格温顺忠诚，体能良好，适应高原环境，是本土优秀犬种。"},
"silky_terrier": {"cn": "丝毛梗", "origin": "澳大利亚", "features": "长有如丝绸般顺滑光亮的修长被毛，外观精致美观。性格活泼开朗，好动爱玩，精力充沛，动作灵活机敏，互动性强，是可爱的小型陪伴犬。"},
"soft-coated_wheaten_terrier": {"cn": "软毛小麦梗", "origin": "爱尔兰", "features": "被毛柔软蓬松，质感独特，整体模样温顺可爱。性格热情洋溢，待人友好亲和，性情开朗乐观，情绪稳定，亲和力强，陪伴体验极佳。"},
"west_highland_white_terrier": {"cn": "西高地白梗", "origin": "英国", "features": "通体纯白被毛蓬松柔软，外形俏皮可爱。性格坚韧顽强，元气满满，活力十足，机警灵敏，性格开朗，适应力强，深受大众喜爱。"},
"lhasa": {"cn": "拉萨犬", "origin": "中国西藏", "features": "被毛浓密修长，体态优雅古朴，是传统本土犬种。警惕性极强，戒备心重，感官敏锐，忠诚护主，性格沉稳，擅长守护家园，适应高原气候。"},
"flat-coated_retriever": {"cn": "平毛寻回犬", "origin": "英国", "features": "被毛顺滑平整，体态匀称矫健。性格乐观开朗，活泼外向，情绪积极，精力充沛，待人友善温顺，服从性佳，是优秀的工作犬与家庭伴侣犬。"},
"curly-coated_retriever": {"cn": "卷毛寻回犬", "origin": "英国", "features": "全身布满卷曲的被毛，造型独特。性格独立沉稳，有自己的判断，行动稳健，嗅觉与寻回能力出众，耐力良好，工作状态稳定可靠。"},
"golden_retriever": {"cn": "金毛寻回犬", "origin": "英国", "features": "毛发金黄靓丽，体态匀称大气。智商出众，学习能力强，性情友善温顺，待人包容，脾气极好，忠诚度高，是家喻户晓的全能型伴侣与工作犬。"},
"labrador_retriever": {"cn": "拉布拉多犬", "origin": "加拿大", "features": "躯体结实匀称，体态干练利落。性格极为忠诚，待人友善温和，亲和力拉满，情绪稳定，服从性优秀，广泛应用于导盲、搜救等各类工作领域。"},
"chesapeake_bay_retriever": {"cn": "切萨皮克湾寻回犬", "origin": "美国", "features": "背部被毛厚实且具备优秀的防水性能，擅长水上作业。体格强壮，耐力持久，性格坚毅勇敢，嗅觉灵敏，寻回能力突出，适应水陆环境。"},
"german_short-haired_pointer": {"cn": "德国短毛指示犬", "origin": "德国", "features": "体态匀称矫健，身体机能出色，是公认的全能型猎犬。反应敏捷，嗅觉优异，服从性强，耐力充沛，既能野外狩猎，也可作为家庭陪伴犬。"},
"vizsla": {"cn": "维兹拉犬", "origin": "匈牙利", "features": "体态优雅流畅，线条优美。性格十分黏人，极度依赖主人，忠心不二，性情温顺和善，动作灵活，嗅觉出众，狩猎与陪伴能力兼备。"},
"english_setter": {"cn": "英国塞特犬", "origin": "英国", "features": "身形高挑优雅，步态从容大气，尽显绅士风范。性格温顺平和，举止端庄，待人友善，嗅觉灵敏，动作轻盈，是气质出众的狩猎伴侣犬。"},
"irish_setter": {"cn": "爱尔兰塞特犬", "origin": "爱尔兰", "features": "身披鲜艳的鲜红色修长被毛，外观夺目亮眼。体态矫健，精力旺盛，性格活泼开朗，行动敏捷，嗅觉优秀，兼具颜值与实用能力。"},
"gordon_setter": {"cn": "戈登塞特犬", "origin": "英国", "features": "体态魁梧匀称，气质沉稳端庄。性格稳重内敛，具备强烈的守护意识，警惕性高，忠诚可靠，耐力出色，是优秀的护卫犬与狩猎犬。"},
"brittany_spaniel": {"cn": "布列塔尼猎犬", "origin": "法国", "features": "体型中等，体态灵活轻巧，行动敏捷迅速。智商极高，领悟力与服从性俱佳，学习速度快，精力充沛，野外作业能力强，综合表现出色。"},
"clumber": {"cn": "克伦伯猎犬", "origin": "英国", "features": "身躯庞大笨重，体态敦实厚重，动作略显迟缓。性格沉稳冷静，性情温和佛系，耐心十足，嗅觉灵敏，耐力良好，工作态度踏实稳重。"},
"english_springer": {"cn": "英国史宾格犬", "origin": "英国", "features": "体态匀称灵活，四肢矫健有力。性格活泼外向，头脑聪明机灵，反应迅速，嗅觉优异，精力充沛，常被用作搜爆、搜救等专业工作犬。"},
"welsh_springer_spaniel": {"cn": "威尔士史宾格", "origin": "英国", "features": "身形紧凑匀称，动作灵活轻快。天性忠诚专一，对主人不离不弃，体能出色，耐力持久，性格温顺友善，狩猎与陪伴能力都十分优秀。"},
"cocker_spaniel": {"cn": "可卡犬", "origin": "英国", "features": "长有波浪状的垂耳，毛发蓬松柔软，外形甜美可爱。性格温柔细腻，待人亲和友善，性情乖巧，活泼有度，互动性好，是热门的家庭伴侣犬。"},
"sussex_spaniel": {"cn": "萨塞克斯猎犬", "origin": "英国", "features": "体态敦实稳健，行动节奏偏慢，性情悠然佛系。性格温顺安静，情绪平稳，嗅觉能力优秀，耐力尚可，做事踏实，适合安静的饲养环境。"},
"irish_water_spaniel": {"cn": "爱尔兰水猎犬", "origin": "爱尔兰", "features": "全身覆盖浓密卷曲的被毛，防水效果极佳。水性超群，精通各类水下活动，动作灵活，耐力充沛，嗅觉灵敏，是专业的水上狩猎犬。"},
"kuvasz": {"cn": "库瓦兹犬", "origin": "匈牙利", "features": "通体雪白，体型庞大魁梧，是大型守卫犬。体格强悍，气势威严，性格沉稳警惕，忠诚护主，领地意识强，护卫能力十分出众。"},
"schipperke": {"cn": "舒伯齐犬", "origin": "比利时", "features": "体型小巧紧凑，动作轻盈敏捷，身姿灵活。好奇心格外强烈，对外界事物充满探索欲，性格机敏活泼，警惕性高，陪伴趣味性十足。"},
"groenendael": {"cn": "比利时牧羊犬", "origin": "比利时", "features": "身披修长浓密的长毛，外形英气十足。头脑聪慧机敏，理解能力强，服从性好，行动敏捷，耐力充沛，是全能型的工作与护卫犬。"},
"malinois": {"cn": "马里努阿犬", "origin": "比利时", "features": "体态干练矫健，爆发力强，动作迅猛。综合能力顶尖，反应敏锐，执行力出色，耐力持久，服从度高，凭借硬实力成为全球公认的顶级警犬。"},
"briard": {"cn": "伯瑞犬", "origin": "法国", "features": "浓密长毛覆盖全身，身形高大壮硕。是优秀的长毛守卫犬，性格沉稳忠诚，警惕性强，体能充沛，既能看护家园，也可陪伴家人生活。"},
"kelpie": {"cn": "卡尔比犬", "origin": "澳大利亚", "features": "体态精干利落，行动力拉满，被称作天生的工作狂。精力永不枯竭，专注力强，服从性佳，擅长畜牧工作，吃苦耐劳，工作效率极高。"},
"komondor": {"cn": "可蒙犬", "origin": "匈牙利", "features": "被毛蓬松缠绕如同拖把一般，外形极具特色。体型庞大，性格勇敢无畏，气场强大，忠诚护主，领地意识浓厚，是出色的大型护卫犬。"},
"old_english_sheepdog": {"cn": "古英国牧羊犬", "origin": "英国", "features": "全身被毛浓密蓬松，毛发丰厚厚实，体态圆润憨厚。性格温顺沉稳，待人友善，行动稳健，亲和力强，历史悠久，经典的畜牧伴侣犬。"},
"shetland_sheepdog": {"cn": "喜乐蒂牧羊犬", "origin": "英国", "features": "体型小巧精致，体态优雅匀称。头脑聪慧过人，忠诚度极高，心思细腻，服从性优秀，性格温顺活泼，兼具陪伴与畜牧工作能力。"},
"collie": {"cn": "柯利牧羊犬", "origin": "英国", "features": "身形修长优雅，体态端庄大气，是经典影视形象莱西的原型。智商高，性情温和忠诚，感知敏锐，行动灵活，畜牧与陪伴表现都很优秀。"},
"border_collie": {"cn": "边境牧羊犬", "origin": "英国", "features": "在所有犬种中智商排名第一，头脑聪慧绝顶，领悟力超强。学习速度极快，服从性好，精力旺盛，动作灵活，是顶尖的畜牧犬与竞技犬。"},
"bouvier_des_flandres": {"cn": "法兰德斯牧牛犬", "origin": "比利时", "features": "身躯粗壮结实，肌肉发达，力量感十足。体格强悍，性格沉稳坚毅，耐力持久，服从性良好，擅长牧牛与护卫，工作能力扎实可靠。"},
"rottweiler": {"cn": "罗威纳犬", "origin": "德国", "features": "体态壮硕有力，骨架粗壮，气势沉稳。性格冷静内敛，身手强悍，警惕性高，忠诚护主，攻防能力兼备，是全球知名的护卫犬与工作犬。"},
"german_shepherd": {"cn": "德国牧羊犬", "origin": "德国", "features": "体态匀称挺拔，线条利落，综合能力全面。反应敏锐，服从性极佳，适应力强，可胜任警犬、搜救犬、护卫犬等多种岗位，是全能工作犬。"},
"doberman": {"cn": "杜宾犬", "origin": "德国", "features": "身形流畅干练，体态优雅矫健，气场十足。性格警觉敏锐，观察力出众，反应迅速，行动力强，智商高，忠诚可靠，多用于护卫与警务工作。"},
"miniature_pinscher": {"cn": "迷你杜宾", "origin": "德国", "features": "体型小巧玲珑，体态精致挺拔，动作利落。性格勇敢大胆，胆量远超自身体型，机警灵敏，精力充沛，行动轻快，警惕性十足。"},
"greater_swiss_mountain_dog": {"cn": "大瑞士山地犬", "origin": "瑞士", "features": "体型高大魁梧，身躯结实强壮，体能充沛。性格沉稳踏实，力量十足，耐力持久，性情温顺忠诚，擅长山地劳作与家园护卫工作。"},
"bernese_mountain_dog": {"cn": "伯恩山犬", "origin": "瑞士", "features": "体态壮硕匀称，毛色搭配美观大气。性格温和敦厚，待人友善包容，情绪稳定，忠诚度高，耐力良好，是温柔可靠的大型伴侣与工作犬。"},
"appenzeller": {"cn": "阿彭策尔山地犬", "origin": "瑞士", "features": "体态矫健灵活，四肢有力，行动十分敏捷。精力旺盛，性格活泼开朗，适应山地复杂环境，耐力出色，忠诚听话，工作积极性很高。"},
"entlebucher": {"cn": "恩特雷布赫山地犬", "origin": "瑞士", "features": "身形紧凑结实，体态干练，活力满满。性格活跃好动，行动力强，反应灵敏，吃苦耐劳，适应山地生活，是优秀的小型山地工作犬。"},
"boxer": {"cn": "拳师犬", "origin": "德国", "features": "躯体肌肉饱满，体态健壮有力。性格活泼开朗，天生爱玩闹，心态乐观，待人友善，动作灵活，忠诚度高，陪伴与护卫能力兼备。"},
"bull_mastiff": {"cn": "斗牛獒", "origin": "英国", "features": "体型硕大壮硕，属于巨型护卫犬，外形威慑力极强。性格冷静自信，情绪稳定，警惕性高，沉稳内敛，护主心切，守护家园能力突出。"},
"tibetan_mastiff": {"cn": "藏獒", "origin": "中国", "features": "体型庞大威猛，被毛浓密厚实，气场强大。性格独立孤傲，体魄强悍勇猛，忠诚度极高，领地意识强烈，是传统的高原护卫犬。"},
"french_bulldog": {"cn": "法国斗牛犬", "origin": "法国", "features": "体态短小精悍，肌肉发达紧实，身形敦实可爱。性格安静温顺，不爱大声吠叫，运动量需求小，性情佛系，非常适合城市室内饲养。"},
"great_dane": {"cn": "大丹犬", "origin": "德国", "features": "体型高大魁梧，身姿挺拔优雅，是知名巨型犬。体态优美大气，性格温顺谦和，举止沉稳，外表霸气内心温柔，观赏性与陪伴感兼具。"},
"saint_bernard": {"cn": "圣伯纳犬", "origin": "瑞士", "features": "身躯庞大厚重，毛发浓密厚实。性情仁慈温顺，待人宽厚友善，耐心十足，历史上曾救助雪山遇险人员，是温柔的大型救援犬。"},
"eskimo_dog": {"cn": "爱斯基摩犬", "origin": "北极", "features": "被毛浓密厚实，双层毛发结构抵御严寒。天生耐寒能力极强，适应极寒的北极环境，体态矫健，耐力充沛，性格机敏忠诚。"},
"malamute": {"cn": "阿拉斯加雪橇犬", "origin": "美国", "features": "体型高大壮硕，骨架粗大，肌肉发达。力量无穷，负重与拉拽能力顶尖，耐力持久，性格憨厚温顺，是经典的极地雪橇工作犬。"},
"siberian_husky": {"cn": "哈士奇", "origin": "俄罗斯", "features": "外形俊美灵动，神态有趣，性格活泼搞怪。精力异常旺盛，整日活力满满，运动量需求大，好奇心重，性格开朗，自带搞笑特质。"},
"affenpinscher": {"cn": "艾芬品", "origin": "德国", "features": "面部样貌酷似猴子，因此也被称作猴面梗，外形诙谐有趣。体型小巧，动作灵活，性格机敏警惕，活泼好动，忠诚度高，互动趣味十足。"},
"basenji": {"cn": "巴森吉犬", "origin": "刚果", "features": "拥有特殊的生理特点，是几乎不会吠叫的犬种。体态轻盈优雅，动作敏捷，性格独立聪慧，爱干净，警惕性强，野外生存能力出色。"},
"pug": {"cn": "八哥犬", "origin": "中国", "features": "面部褶皱明显，体态圆润憨厚，模样呆萌可爱。性格温和敦厚，风趣幽默，性情安静慵懒，运动量小，待人友善，是经典的本土伴侣犬。"},
"leonberg": {"cn": "兰伯格犬", "origin": "德国", "features": "体型庞大壮硕，外形神似雄狮，气势威严。性格温顺沉稳，待人友善，忠诚度高，体能充沛，耐力良好，兼具护卫与陪伴双重属性。"},
"newfoundland": {"cn": "纽凡兰犬", "origin": "加拿大", "features": "身躯庞大强健，水性天赋出众，素有水中救生员的称号。性格温柔善良，耐心十足，力量强大，擅长水上救援，性情稳重可靠。"},
"great_pyrenees": {"cn": "大白熊犬", "origin": "法国", "features": "通体雪白，毛发蓬松丰厚，体型高大。警惕性强，领地意识明显，是能力出色的守卫犬，性格温顺忠诚，对家人十分友善包容。"},
"samoyed": {"cn": "萨摩耶犬", "origin": "俄罗斯", "features": "毛发洁白蓬松，面带笑意，被称作微笑天使。性格开朗活泼，温顺亲人，待人友善，精力充沛，颜值出众，是人气极高的伴侣犬。"},
"pomeranian": {"cn": "博美犬", "origin": "德国", "features": "体型娇小玲珑，毛发浓密蓬松，外形精致可爱。性格机敏活泼，警惕性较强，动作轻快，粘人可爱，运动量适中，深受宠物爱好者喜爱。"},
"chow": {"cn": "松狮犬", "origin": "中国", "features": "体态敦实厚重，拥有标志性的紫色舌头，外形辨识度极高。性格沉稳独立，举止慵懒淡定，忠诚护主，毛发厚实，适应能力较强。"},
"keeshond": {"cn": "荷兰毛狮犬", "origin": "荷兰", "features": "毛发浓密丰厚，体态圆润饱满。性格友善温和，待人热情亲切，情绪稳定，不爱吵闹，观察力敏锐，陪伴氛围轻松愉悦。"},
"brabancon_griffon": {"cn": "布鲁塞尔格里芬", "origin": "比利时", "features": "面部神态生动鲜活，表情丰富多变，外形独特讨喜。头脑聪明伶俐，理解能力强，性格机敏好动，警惕性高，互动灵活，陪伴体验很好。"},
"pembroke": {"cn": "彭布罗克柯基", "origin": "英国", "features": "四肢短小修长，臀部圆润可爱，标志性短尾极具特点。性格活泼开朗，元气满满，动作灵活，温顺亲人，运动量较大，人气居高不下。"},
"cardigan": {"cn": "卡迪根柯基", "origin": "英国", "features": "四肢短矮，身形修长，保留完整长尾，体态稳重。性格沉稳内敛，心思细腻，警惕性佳，忠诚度高，适应力强，性情温和安静。"},
"toy_poodle": {"cn": "玩具贵宾", "origin": "法国", "features": "体型小巧精致，体态优雅灵动。智商位居犬类前列，头脑聪慧，学习能力强，性格活泼温顺，造型多变，是热门的小型伴侣犬。"},
"miniature_poodle": {"cn": "迷你贵宾", "origin": "法国", "features": "体型适中，体态比例匀称，综合表现均衡全面。智商高，服从性好，性格活泼有度，温顺亲人，易训练，兼顾颜值与实用性。"},
"standard_poodle": {"cn": "标准贵宾", "origin": "法国", "features": "身形高挑挺拔，姿态优雅大气，举止端庄。头脑聪慧，反应敏捷，耐力出色，性格沉稳友善，工作与陪伴能力都十分优秀。"},
"mexican_hairless": {"cn": "墨西哥无毛犬", "origin": "墨西哥", "features": "体表大多无被毛，外形独特另类。性格忠心耿耿，极度依恋主人，性情温顺安静，体质特殊，适应能力较强，是小众特色伴侣犬。"},
"dingo": {"cn": "澳洲野犬", "origin": "澳大利亚", "features": "体态矫健接近原生犬类，野性十足。性格独立坚韧，自主生存能力强，行动敏捷，警惕性高，群居生活，野外适应能力极其出色。"},
"dhole": {"cn": "亚洲豺犬", "origin": "亚洲", "features": "身形矫健灵活，擅长群体活动，社会性极强。团队协作能力突出，行动敏捷，耐力持久，狩猎配合默契，野外生存本领高强。"},
"african_hunting_dog": {"cn": "非洲野犬", "origin": "非洲", "features": "群体生活模式为主，是天生的团队型猎手。分工明确，配合默契，奔跑速度快，耐力惊人，野性十足，狩猎效率位居前列。"},
"giant_schnauzer": {"cn": "巨型雪纳瑞", "origin": "德国", "features": "体型高大壮硕，被毛粗硬有型。性格勇敢坚毅，意志力顽强，警惕性高，忠诚护主，执行力强，是优秀的大型工作护卫犬。"},
"standard_schnauzer": {"cn": "标准雪纳瑞", "origin": "德国", "features": "体态中等匀称，结构紧凑合理。性格沉稳机敏，综合素质优秀，服从性良好，适应多种工作场景，是公认的理想全能工作犬。"},
"default": {"cn": "独特品种", "origin": "全球分布", "features": "这类犬种分布于世界各地，拥有各自独特的优良品性。大多性格活泼开朗，对主人忠诚专一，体质健康，适应力强，陪伴与实用价值兼备。"}
}

# --- 数据库模型 ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='normal') 
    records = db.relationship('History', backref='owner', lazy=True)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    breed = db.Column(db.String(50))
    conf = db.Column(db.String(20))
    img_name = db.Column(db.String(100))
    origin = db.Column(db.String(100))
    time = db.Column(db.DateTime, default=datetime.now)

with app.app_context(): db.create_all()

# --- 后端核心业务接口 ---
@app.route('/')
def index(): return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    f = request.files['file']
    try:
        img_bytes = f.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        res = predict_dog(img)
        b_en = res["breed"].lower()
        info = DOG_WIKI.get(b_en, DOG_WIKI["default"])
        c_pct = f"{res['confidence'] * 100:.2f}%"
        img_name = str(uuid.uuid4()) + ".jpg"
        if not os.path.exists('static/uploads'): os.makedirs('static/uploads')
        img.save(os.path.join('static/uploads', img_name))
        if 'u_id' in session:
            h = History(user_id=session['u_id'], breed=info['cn'], conf=c_pct, img_name=img_name, origin=info['origin'])
            db.session.add(h); db.session.commit()
        return jsonify({"success": True, "breed_cn": info['cn'], "confidence_pct": c_pct, "origin": info["origin"], "features": info["features"], "breed_en": b_en})
    except Exception as e: return jsonify({"success": False, "error": str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    u = User.query.filter_by(username=d['username']).first()
    if u and check_password_hash(u.password, d['password']):
        session['u_id'], session['u_name'], session['is_admin'] = u.id, u.username, u.is_admin
        return jsonify({"success": True, "username": u.username, "is_admin": u.is_admin})
    return jsonify({"success": False, "message": "账户或密码错误"})

@app.route('/api/register', methods=['POST'])
def register():
    d = request.json
    is_first = User.query.count() == 0
    u = User(username=d['username'], password=generate_password_hash(d['password']), is_admin=is_first)
    db.session.add(u); db.session.commit()
    return jsonify({"success": True})

@app.route('/api/check_login')
def check_login():
    if 'u_id' in session:
        u = User.query.get(session['u_id'])
        return jsonify({"is_logged_in": True, "username": u.username, "is_admin": u.is_admin, "status": u.status})
    return jsonify({"is_logged_in": False})

@app.route('/api/admin/stats')
def admin_stats():
    return jsonify({"total_users": User.query.count(), "total_images": History.query.count()})

@app.route('/api/admin/all_logs')
def admin_logs():
    logs = History.query.order_by(History.time.desc()).limit(30).all()
    data = []
    for l in logs:
        u = User.query.get(l.user_id)
        data.append({"user": u.username if u else "未知", "breed": l.breed, "conf": l.conf, "time": l.time.strftime("%H:%M"), "img": l.img_name})
    return jsonify({"success": True, "data": data})

@app.route('/api/admin/pendings')
def get_pendings():
    users = User.query.filter_by(status='pending').all()
    return jsonify({"success": True, "data": [{"id": x.id, "name": x.username} for x in users]})

@app.route('/api/admin/approve', methods=['POST'])
def approve():
    u = User.query.get(request.json.get('user_id'))
    if u: u.is_admin = True; u.status = 'normal'; db.session.commit()
    return jsonify({"success": True})

@app.route('/api/apply_admin', methods=['POST'])
def apply_admin():
    u = User.query.get(session.get('u_id')); u.status = 'pending'; db.session.commit()
    return jsonify({"success": True})

@app.route('/api/history')
def get_history():
    recs = History.query.filter_by(user_id=session['u_id']).order_by(History.time.desc()).all()
    return jsonify({"success": True, "data": [{"breed": r.breed, "conf": r.conf, "time": r.time.strftime("%m-%d %H:%M"), "img": r.img_name, "origin": r.origin} for r in recs]})

@app.route('/api/logout')
def logout(): session.clear(); return jsonify({"success": True})

if __name__ == '__main__':
    # 强制监听 0.0.0.0 允许 IP 访问
    app.run(host='0.0.0.0', port=5000, debug=True)
