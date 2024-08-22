# -*- coding: utf-8 -*-
import os
import qianfan
import json
#【推荐】使用安全认证AK/SK鉴权，通过环境变量初始化认证信息
# 替换下列示例中参数，安全认证Access Key替换your_iam_ak，Secret Key替换your_iam_sk
os.environ["QIANFAN_ACCESS_KEY"] = "***"
os.environ["QIANFAN_SECRET_KEY"] = "***"

sys_promt_head='您现在是面向儿童的绘本阅读辅助智能台灯的语音助手。您的任务是接收用户通过文字输入的指令，理解其意图，并生成一个字典格式的回复。这个回复需要包含以下三个部分：      1. **理解状态** (`is_understood`): 一个布尔值，`true`表示完全理解用户的操作要求，`false`则表示存在理解上的困难或无法执行。      2. **执行功能列表** (`actions`): 一个字符串数组，用于详细列出台灯需要执行的具体功能。每个功能作为数组的一个元素，确保台灯的程序能够准确识别并执行。'

#通过编辑这部分修改对应关系,后面为了代码方便返回一个整型亦可
sys_promt_body='具体功能语义与字符串对应关系如下：{“把灯光调亮”：“add_brightness”,“把灯光调暗”：“decrease_brightness","播放音乐"：“play_music”,"描述绘本内容"：“describe”，“描述文字内容”：“read_out”}，如果没有上表中的内容，则返回一个空数组，，“is_understood”也应该为false'


sys_promt_tail='3. **回复内容** (`response`): 一个字符串，用于向用户展示儿童式的友好、清晰、有幼稚感的回复信息，反馈的执行功能重点参考实际执行情况而非要求。      **示例输入**（用户文字指令）:"这一页讲了什么呀,告诉我好吗。"      **示例输出**（字典格式回复）:   {"is_understood": true, "actions": ["describe",“read_out”], "response": "好呀，小朋友，我来给你讲讲这一页的图画和文字。"}    现在，请基于以下用户输入，生成仅仅含有相应字典格式的回复，千万别换行：'

sys_promt=sys_promt_head+sys_promt_body+sys_promt_tail

#将AI模型返回的json格式字符串转换成Python字典
def json_str2dic(input_str):
    # 去除包裹的 ```json 和 ``` 标记
    clean_str = input_str.strip('```json').strip('```')

    # 去除多余的换行符和空格，得到标准 JSON 字符串
    json_str = clean_str.replace('\n', '').replace('    ', '')

    # 将 JSON 字符串转换为 Python 字典
    result_dict = json.loads(json_str)

    return result_dict

def response(word):
    chat_comp = qianfan.ChatCompletion()
    # 指定特定模型为ERNIE-4.0-Turbo-8K
    resp = chat_comp.do(
        model="ERNIE-4.0-Turbo-8K", messages=[{
            "role": "user",
            "content": word
    }],
        system=sys_promt,
        #stream默认为False,这里只是为了突出，如果改为True,resp变为包括逐步更新的若干短回复，好处是生成时间短
        stream=False)
    
    resp_dic=json_str2dic(resp["body"]["result"])
    return resp_dic



if __name__ == "__main__":
    result_dic=response("我是李明明")
    print(result_dic)
    print(result_dic["is_understood"])
    input("Press Enter to exit...")