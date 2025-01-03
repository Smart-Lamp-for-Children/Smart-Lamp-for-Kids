from openai import OpenAI
import os
import json

os.environ["DASHSCOPE_API_KEY"] = "sk-fa7af4f6e4ca4060bf4cd1e5d2915aa5"
def get_response(api_key: str, image_url: str, task: str):
    """
    image_url: 传入图片链接
    task: 任务类型，可选类型：word_recognition, image_description
    """
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    if task == "word_recognition":
        sys_prompt = "你是一个文字识别助手，能够提取出图片里的文字。"
        user_prompt = "请提取出图片中的文字内容并输出。"
    elif task == "image_description":
        sys_prompt = "你是帮助小朋友理解绘本内容的智能助手。"
        user_prompt = "请你向小朋友描述图片中的画面内容，尽量如实描述。"
    
    completion = client.chat.completions.create(
        model="qwen-vl-max",
        messages=[
            {
                "role": "system",
                "content": sys_prompt
            },
            {
              "role": "user",
              "content": [
                {
                  "type": "text",
                  "text": user_prompt
                },
                {
                  "type": "image_url",
                  "image_url": {
                    "url": image_url
                  }
                }
              ]
            }
          ],
        top_p=0.8,
    )
    response = completion.model_dump_json()
    response = json.loads(response)
    return response["choices"][0]["message"]["content"]

if __name__=='__main__':
    image_link = "https://i.ibb.co/J5YVB3s/2024-12-17-22-26-15.png"
    print(get_response(os.getenv("DASHSCOPE_API_KEY"), image_link, "word_recognition"))