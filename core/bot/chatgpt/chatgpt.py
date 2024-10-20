from openai import OpenAI
import os


class OpenAIChatClient:
    def __init__(self, api_key=None):
        """
          初始化 OpenAI API 客户端，可以通过环境变量或者传入 api_key
          """

        self.api_key = api_key or "sk-GZmletEW0sn8Kp7tA33f9a00C4Fd4a3a9848C12080C74c9d"
        self.api_base = "https://oneapi.sotawork.com/v1"


        # 初始化 OpenAI 客户端
        self.client = OpenAI(api_key=self.api_key,base_url=self.api_base)

    def get_response(self, prompt, model="gpt-4o-mini", response_format="json"):
        """
          发送 prompt 给 OpenAI，并返回结果（JSON格式）
          """
        try:
            # 生成完成的响应
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": '你是一个AI助手，将用JSON格式返回.且键固定为英文，值可以是中文、英文、数字、符号等。'},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            # 获取回答内容
            response_content = completion.choices[0].message.content
            return response_content

        except Exception as e:
            print(f"请求出错: {e}")
            return None


# 示例用法
if __name__ == "__main__":
    api_key = "sk-7Vl54xxxxxxxxxxxxxxx"  # 你的 API Key
    client = OpenAIChatClient()

    prompt = "中国首都是哪里？"
    response = client.get_response(prompt)

    if response:
        print("AI 回复:", response)
