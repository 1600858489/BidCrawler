import base64
import json

from openai import OpenAI

from prompt import *


class OpenAIChatClient:
    def __init__(self, api_key=None):
        """
          初始化 OpenAI API 客户端，可以通过环境变量或者传入 api_key
          """

        self.api_key = api_key or "sk-GZmletEW0sn8Kp7tA33f9a00C4Fd4a3a9848C12080C74c9d"
        self.api_base = "https://oneapi.sotawork.com/v1"


        # 初始化 OpenAI 客户端
        self.client = OpenAI(api_key=self.api_key,base_url=self.api_base)

    def image_to_base64(self, image_path):
        """
        将图片转换为 Base64 编码
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')



    def get_response(self, prompt, model="gpt-4o-mini", response_format="json"):
        """
          发送 prompt 给 OpenAI，并返回结果（JSON格式）
          """
        try:
            # 生成完成的响应
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": PROMPT_TEMPLATE},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            # 获取回答内容
            response_content = completion.choices[0].message.content
            try:
                response_content = eval(response_content)
                response_content = json.dumps(response_content, ensure_ascii=False)
                return response_content
            except:
                return None

        except Exception as e:
            print(f"请求出错: {e}")
            return None

    def upload_image(self, image_path):
        """
        上传图片并返回识别结果
        """
        with open(image_path, "rb") as f:
            response = self.client.upload(f)
            return response.get("image_url")


# 示例用法
if __name__ == "__main__":
    api_key = "sk-7Vl54xxxxxxxxxxxxxxx"  # 你的 API Key
    client = OpenAIChatClient()

    prompt = """
金汤小米烩三宝
菜品介绍
金汤小米烩三宝是一道宴请上等贵宾的客家菜。此菜品以南瓜翅汤为基底，小米为主料，搭配三种风味独特的鲜美食材，如海参，鱼肚，鱼翅。金黄色的南瓜翅汤和小米相得益彰，色泽金黄，口感浓郁。此菜不仅容易消化，还富含多种维生素和矿物质

原料
小米：
南瓜茸：
海参：
鱼肚：
翅汤；
鱼翅；
青豆：
姜葱
盐：适量
白胡椒粉：适量
鸡精：适量
淀粉：适量
 黄酒
清水：适量

做法

1. 小米淘洗干净，用清水浸泡30分钟备用。
2. 南瓜去皮去籽，切成小块，蒸熟制成茸。
3. 海参，鱼肚切块

1. 在锅中加入适量清水，加姜葱料酒，放入海参鱼肚，大火煮沸后倒出沥干水份。

2.取锅加入翅汤，南瓜茸调色，
加入盐、白胡椒粉和鸡精调味，加入海参鱼肚，鱼翅，青豆，煮至入味勾芡即可关火出锅装盘即可。

营养功效
金汤小米烩三宝富含蛋白质、膳食纤维、维生素A、维生素C以及多种矿物质，具有开胃健脾、养胃护胃的功效。

进程已结束，退出代码为 0
        """
    response = client.get_response(prompt)

    if response:
        print("AI 回复:", response)