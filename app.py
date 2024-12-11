from flask import Flask, render_template, request
import openai



app = Flask(__name__)

# 設定 OpenAI API 金鑰
openai.api_key = "sk-F9lrK50rajE8f4FUCaFf48078cB448Bd958aB45dD30d4912"
# 用free api key做中轉 若無則不須啟用
openai.api_base = "https://free.v36.cm/v1"

# 縣市與區域資料
taiwan_regions = {
    "台北市": ["中正區", "大同區", "中山區", "松山區", "大安區", "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"],
    "台中市": ["中區", "東區", "南區", "西區", "北區", "北屯區", "西屯區", "南屯區"],
    "高雄市": ["新興區", "前金區", "苓雅區", "鹽埕區", "鼓山區", "旗津區", "前鎮區", "三民區"]
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
