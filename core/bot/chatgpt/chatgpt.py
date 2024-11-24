import json

from openai import OpenAI

try:
    from .prompt import *
except:
    from prompt import *

from log.logger import Logger

log = Logger().get_logger()

class OpenAIChatClient:
    def __init__(self, api_key=None, api_base=None):
        """
          初始化 OpenAI API 客户端，可以通过环境变量或者传入 api_key
          """
        if not api_key:
            raise ValueError("请设置环境变量 OPENAI_API_KEY 或传入 api_key 参数")

        self.api_key = api_key
        if api_base:
            self.api_base = api_base

        # 初始化 OpenAI 客户端
        self.client = OpenAI(api_key=self.api_key,base_url=self.api_base)

    def get_response(self, prompt, images=None, model="gpt-4o", response_format="json", template=1) -> dict or None:
        """
          发送 prompt 给 OpenAI，并返回结果（JSON格式）
          """
        if images is None:
            images = []

        try:
            # 生成完成的响应
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": PROMPT_RENT if template == 1 else PROMPT_PREFORM},
                    {"role": "user", "content": [{"type": "text", "text": prompt}] + [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}} for image in
                        images]}
                ],
                stream=False,
                response_format={"type": "json_object"}
            )

            response_content = completion.choices[0].message.content
            log.debug(f"AI 回复: {response_content}")
            try:
                response_content = json.loads(response_content)
                return response_content
            except:
                response_content = json.loads(response_content)
                return response_content

        except Exception as e:
            print(f"请求出错: {e}")
            log.error(f"请求出错: {e}")
            return None


# 示例用法
if __name__ == "__main__":
    api_key = "sk-tAVPzckqsRVj6p7u726025D2Fc17476f82Be56C0517f5005"  # 你的 API Key
    client = OpenAIChatClient(
        api_key=api_key,
        api_base="https://api.xty.app/v1"
    )

    prompt = """
    检查文件
        """
    from core.file_read.pdf import *

    images = read_pdf(r"E:\电纸书\杭州港萧山港区临浦作业区（一期）项目施工监理中标前公示.pdf",
                      poppler_path=r'F:\python_projcet\BidCrawler\poppler\Library\bin')

    for i in range(10):
        response = client.get_response(prompt, images=images, template=1)

        if response:
            # print("AI 回复:", response)
            print(type(response))
