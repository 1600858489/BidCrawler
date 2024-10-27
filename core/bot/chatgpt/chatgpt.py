from openai import OpenAI
import os

from prompt import  *


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
                    {"role": "system", "content": PROMPT_TEMPLATE},
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

    prompt = """
    建设工程中标通知书台州市建设咨询有限公司：经评标委员会评审及中标候选人公示，现确定贵单位中标。请收到本通知书30天内，到我单位签订建设工程合同。特此通知。招标项目黄岩区江口街道白云山西路南侧、应家山路西侧地块房产建设项目(全过程工程咨询)备案登记号台建招备[2024]2084号招标方式公开招标招标人台州新跃建设有限公司招标代理机构台州市建航工程管理有限公司招标内容招标范围及招标内容具体如下：全过程造价控制具体如下：预算审核，施工过程进度款、变更、签证、索赔经济性审核，无价材料清单审核、询价、组价、定价谈判，参与主要设备/材料市场考察，结算审核复核、资金计划编制/审核，投资动态台账管理，出现投资控制异常情况预警并协助建设单位提出有效建议及措施。施工阶段监理：配合项目前期准备工作、施工阶段全过程监理、配合结算审核及保修阶段的监理，包括施工管理及移交管理，对整个工程建设的质量、进度、投资、安全、合同、信息及组织协调所有方面进行全面控制和管理、工程保修期内的缺陷修复督促管理，具体监理工作按《建设工程监理规范》（GB50319-2013）、《房屋建筑和市政基础设施工程竣工验收规定》及《施工旁站监理管理办法》组织实施。建设规模项目总用地面积24564㎡，总建筑面积约75740㎡。容积率≤2.2，地上建筑面积≤54040㎡（含物业等相关配套用房），建筑密度≤30%，建筑高度≤60m（自室外地坪算起，其中住宅建筑高度≥36m）。回购房屋用房建筑面积≥52200㎡（不含物业等相关配套用房，至少522套），要求A套型(建筑面积60㎡)≥72套，B套型(建筑面积80㎡)≥162套，C型(建筑面积100㎡)≥72套，D型(建筑面积120㎡)≥108 套，E型(建筑面积 137㎡)≥108 套。中标人台州市建设咨询有限公司项目总负责人牟汉林中标价(元)3192983质量标准（1）提供符合现行规范、标准及设计要求项目产品的高质量咨询服务；（2）合理控制项目造价、质量、安全、工期，通过竣工验收且满足招标人对本项目的质量要求。服务期自发出中标通知书之日起，至本项目质量缺陷期（24个月）满后6个月。备注项目负责人：牟汉林证书号：33006895身份证号码：330106********0011招标代理（盖章）：招标人（盖章）：监管部门（盖章）：招标代理项目负责人：王华萍2024年10月24
    """
    response = client.get_response(prompt)

    if response:
        print("AI 回复:", response)
