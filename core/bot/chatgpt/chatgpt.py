import json
from typing import Optional, List, Union

from openai import OpenAI

try:
    from .prompt import *
except:
    from prompt import *

from log.logger import Logger

log = Logger().get_logger()
from pydantic import BaseModel


class Template1(BaseModel):
    section_id: Optional[str]
    section_name: Optional[str]
    project_manager: Optional[str]
    winning_price: Optional[str] 
    duration_days: Optional[str] 
    review_expert: Optional[int] 
    experts: Optional[List[str]] 
    other: Optional[str]


class Template2(BaseModel):
    section_id: Optional[str]
    project_name: Optional[str]
    company_name: Optional[List[str]]
    project_manager: Optional[str]
    price: Optional[List[str]]
    duration_days: Optional[List[str]]
    score: Optional[List[str]]


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
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)

            print("API Key:", self.api_key)
            print("API Base:", self.api_base)
        else:
            self.client = OpenAI(api_key=self.api_key)
            print("API Key:", self.api_key)



        print("OpenAI 客户端初始化成功")


    def get_response(self, prompt, images=None, model="gpt-4o", response_format="json", template=1,
                     max_retries=3) -> dict or None:
        if images is None:
            images = []

        attempt = 0  # 初始化尝试次数

        while attempt < max_retries:
            try:
                # 生成完成的响应
                print(len(prompt),len(images))
                completion = self.client.beta.chat.completions.parse(
                    model=model,
                    messages=[
                        {"role": "system", "content": PROMPT_RENT if template == 1 else PROMPT_PREFORM},
                        {"role": "user", "content": prompt}  # 修改这里
                    ],
                    response_format=Template1 if template == 1 else Template2,
                    timeout=600,

                )

                response_content = completion.choices[0].message.parsed
                log.debug(f"AI 回复: {response_content}")
                print(f"AI 回复: {response_content}")

                return response_content.__dict__ if isinstance(response_content, BaseModel) else {}

            except Exception as e:
                attempt += 1  # 增加尝试次数
                print(f"请求出错: {e}, 正在尝试重试 {attempt}/{max_retries} 次")
                log.error(f"请求出错: {e}")

                if attempt >= max_retries:  # 如果超过最大尝试次数，返回 None
                    print("已达到最大重试次数，放弃请求。")
                    return {}


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

    text, images = read_pdf(r"E:\电纸书\杭州港萧山港区临浦作业区（一期）项目施工监理中标前公示.pdf",
                      poppler_path=r'F:\python_projcet\BidCrawler\poppler\Library\bin')

    for i in range(10):
        response = client.get_response(text, template=1, images=[])

        if response:
            # print("AI 回复:", response)
            print(response)
