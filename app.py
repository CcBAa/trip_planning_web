from flask import Flask, render_template, request
import openai


app = Flask(__name__)

# 設定 OpenAI API 金鑰
openai.api_key = "sk-F9lrK50rajE8f4FUCaFf48078cB448Bd958aB45dD30d4912"
# 用free api key做中轉 若無則不須啟用
openai.api_base = "https://free.v36.cm/v1"

# 縣市與區域資料
taiwan_regions = {
    "台北市": [
        "中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", 
        "北投區", "內湖區", "南港區", "文山區"
    ],
    "新北市": [
        "板橋區", "新莊區", "中和區", "永和區", "土城區", "樹林區", "三峽區", "鶯歌區", 
        "三重區", "蘆洲區", "五股區", "泰山區", "林口區", "八里區", "淡水區", "三芝區", 
        "石門區", "金山區", "萬里區", "汐止區", "瑞芳區", "貢寮區", "平溪區", "雙溪區", 
        "深坑區", "石碇區", "新店區", "坪林區", "烏來區"
    ],
    "基隆市": [
        "中正區", "信義區", "仁愛區", "中山區", "安樂區", "暖暖區", "七堵區"
    ],
    "桃園市": [
        "桃園區", "中壢區", "平鎮區", "八德區", "楊梅區", "大溪區", "蘆竹區", "大園區", 
        "龜山區", "龍潭區", "新屋區", "觀音區", "復興區"
    ],
    "台中市": [
        "中區", "東區", "南區", "西區", "北區", "北屯區", "西屯區", "南屯區", "太平區", 
        "大里區", "霧峰區", "烏日區", "豐原區", "后里區", "石岡區", "東勢區", "和平區", 
        "新社區", "潭子區", "大雅區", "神岡區", "大肚區", "沙鹿區", "龍井區", "梧棲區", 
        "清水區", "大甲區", "外埔區", "大安區"
    ],
    "彰化縣": [
        "彰化市", "鹿港鎮", "和美鎮", "線西鄉", "伸港鄉", "福興鄉", "秀水鄉", "花壇鄉", 
        "芬園鄉", "員林市", "溪湖鎮", "大村鄉", "埔鹽鄉", "埔心鄉", "永靖鄉", "社頭鄉", 
        "田中鎮", "北斗鎮", "田尾鄉", "埤頭鄉", "溪州鄉", "竹塘鄉", "大城鄉", "芳苑鄉", 
        "二林鎮"
    ],
    "南投縣": [
        "南投市", "中寮鄉", "草屯鎮", "國姓鄉", "埔里鎮", "仁愛鄉", "名間鄉", "集集鎮", 
        "竹山鎮", "水里鄉", "魚池鄉", "信義鄉"
    ],
    "台南市": [
        "中西區", "東區", "南區", "北區", "安平區", "安南區", "永康區", "歸仁區", 
        "新化區", "左鎮區", "玉井區", "楠西區", "南化區", "仁德區", "關廟區", "龍崎區", 
        "官田區", "麻豆區", "佳里區", "西港區", "七股區", "將軍區", "學甲區", "北門區", 
        "新營區", "後壁區", "白河區", "東山區", "六甲區", "下營區", "大內區", "山上區", 
        "鹽水區", "善化區", "新市區", "安定區"
    ],
    "高雄市": [
        "新興區", "前金區", "苓雅區", "鹽埕區", "鼓山區", "旗津區", "前鎮區", "三民區", 
        "楠梓區", "小港區", "左營區", "仁武區", "大社區", "岡山區", "路竹區", "橋頭區", 
        "梓官區", "彌陀區", "永安區", "燕巢區", "田寮區", "阿蓮區", "茄萣區", "湖內區", 
        "旗山區", "美濃區", "內門區", "杉林區", "甲仙區", "六龜區", "茂林區", "桃源區", 
        "那瑪夏區"
    ],
    "屏東縣": [
        "屏東市", "潮州鎮", "東港鎮", "恆春鎮", "萬丹鄉", "長治鄉", "麟洛鄉", "九如鄉", 
        "里港鄉", "高樹鄉", "鹽埔鄉", "內埔鄉", "竹田鄉", "新埤鄉", "枋寮鄉", "新園鄉", 
        "崁頂鄉", "林邊鄉", "南州鄉", "佳冬鄉", "琉球鄉", "車城鄉", "滿州鄉", "枋山鄉", 
        "霧台鄉", "瑪家鄉", "泰武鄉", "來義鄉", "春日鄉", "獅子鄉", "牡丹鄉", "三地門鄉"
    ],
    "花蓮縣": [
        "花蓮市", "鳳林鎮", "玉里鎮", "新城鄉", "吉安鄉", "壽豐鄉", "光復鄉", "豐濱鄉", 
        "瑞穗鄉", "萬榮鄉", "卓溪鄉", "富里鄉"
    ],
    "台東縣": [
        "台東市", "成功鎮", "關山鎮", "卑南鄉", "大武鄉", "太麻里鄉", "東河鄉", "長濱鄉", 
        "鹿野鄉", "池上鄉", "綠島鄉", "延平鄉", "海端鄉", "達仁鄉", "金峰鄉", "蘭嶼鄉"
    ],
    "澎湖縣": [
        "馬公市", "西嶼鄉", "望安鄉", "七美鄉", "白沙鄉", "湖西鄉"
    ],
    "金門縣": [
        "金城鎮", "金湖鎮", "金沙鎮", "金寧鄉", "烈嶼鄉", "烏坵鄉"
    ],
    "連江縣": [
        "南竿鄉", "北竿鄉", "莒光鄉", "東引鄉"
    ]
}


def generate_itinerary(city, region):
    prompt = f"請為台灣{city}{region}規劃一個一日行程，包括上午、中午、下午和晚上活動，並附上活動簡要描述。"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一位專業的旅遊規劃師，幫助用戶規劃行程。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except RateLimitError:
        return "OpenAI API 配額已超出，請稍後再試，或檢查帳戶的使用情況。"
    except AuthenticationError:
        return "API 金鑰無效，請檢查你的 OpenAI API 金鑰是否正確。"
    except APIConnectionError:
        return "連接 OpenAI API 時出現問題，請稍後再試。"
    except APIError as e:
        return f"API 發生錯誤：{e}"
    except Exception as e:
        return f"發生未知錯誤：{e}"




@app.route("/", methods=["GET", "POST"])
def index():
    city = None
    region = None
    itinerary = None 

    if request.method == "POST":
        # 從表單獲取選擇的縣市和區域
        city = request.form.get("city")
        region = request.form.get("region")
        if city and region:
            itinerary = generate_itinerary(city, region)  # 調用 AI 生成行程

    return render_template(
        "index.html",
        cities=taiwan_regions.keys(),  # 縣市列表
        regions=taiwan_regions,  # 縣市對應的區域
        itinerary=itinerary,  # AI 生成的行程
        selected_city=city,  # 用戶選中的縣市
        selected_region=region  # 用戶選中的區域
    )

if __name__ == "__main__":
    app.run(debug=True)
