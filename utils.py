import base64
from http import HTTPStatus
import agentscope
import requests
import os
from agentscope.agents import DialogAgent
from agentscope.agents.user_agent import UserAgent
import dashscope

def covert_image_to_base64(image_path):
    # 获得文件后缀名
    ext = image_path.split(".")[-1]
    if ext not in ["gif", "jpeg", "png"]:
        ext = "jpeg"

    with open(image_path, "rb") as image_file:
        # Read the file
        encoded_string = base64.b64encode(image_file.read())

        # Convert bytes to string
        base64_data = encoded_string.decode("utf-8")

        # 生成base64编码的地址
        base64_url = f"data:image/{ext};base64,{base64_data}"
        return base64_url


def generate_image_from_prompt(des):
    import dashscope
    from dashscope.common.error import InvalidTask
    dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY") or dashscope.api_key
    assert dashscope.api_key
    # generate image
    prompt = """根据下面描述:{desc}，生成一张风景图。""".format(des)
    try:
        rsp = dashscope.ImageSynthesis.call(
            model='stable-diffusion-xl', #'wanx-lite',
            prompt=prompt,
            n=1,
            size='256*256')
        # save file to current directory
        if rsp.status_code == HTTPStatus.OK:
            for result in rsp.output.results:
                with open('assets/desc.jpg', 'wb+') as f:
                    f.write(requests.get(result.url).content)
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                (rsp.status_code, rsp.code, rsp.message))
    except InvalidTask as e:
        print(e)

def createimg(description):
    """A basic conversation demo"""
    MY_API_KEY = f"{os.environ.get('DASHSCOPE_API_KEY')}"
    agentscope.init(
        model_configs=[
            {
                "config_name": "my_dashscope_image_synthesis_config",
                "model_type": "dashscope_image_synthesis",

                # Required parameters
                "model_name": "wanx-v1",  # DashScope Image Synthesis API model name, e.g., wanx-v1

                # Optional parameters
                "api_key": MY_API_KEY,
                "generate_args": {
                    "n": 1,
                    "size": "1024*1024"
                    # ...
                }
            },

            {
                "config_name": "my_dashscope_chat_config",
                "model_type": "dashscope_chat",

                # Required parameters
                "model_name": "qwen-max",               # DashScope Chat API model name, e.g., qwen-max

                # Optional parameters
                "api_key": MY_API_KEY,                # DashScope API Key, will be read from environment variables if not provided
                "generate_args": {
                    # e.g., "temperature": 0.5
                },
            },
        ],
    )

    # Init two agents
    INIT_PROMT = "You are a senior product manager, skilled in product design and creating visual prototypes of product appearances."
    dialog_agent = DialogAgent(
        name="Design Assistant",
        sys_prompt=INIT_PROMT,
        model_config_name="my_dashscope_chat_config",  # replace by your model config name
    )
    user_agent = UserAgent()

    # start the conversation between user and assistant

    ### Image generation code ###
    LLM_model = 'qwen-max'
    dashscope.api_key = MY_API_KEY
#    x = user_agent()
#    print("用户输入：",x)

    img_file = 'img.jpg'
    if description == "default":
        print("default value used:白色地中海")
        description = "白色地中海风格"


    instruction = f'''
        generate an english detailed prompt to be used for text to image generation for product. the original prompt is in```
        ```
            一套儿童书桌{description}
        ```
        please return prompt only, less than 100 description, nothing else.
        '''
#        response = Generation.call(
#            model=LLM_model,
#            prompt=instruction
#        )
#        text2image_prompt = response.output['text']
#        print(textwrap.fill(text2image_prompt, width=80))
#        print("instruction is now", instruction)
    dialog_agent.sys_prompt = instruction
    print("提示词现在是：", dialog_agent.sys_prompt)

    x = dialog_agent()
    generate_img_file(x.content,img_file)
#        print("x.content-dialog 现在是：", x.content)




#generate_img_file(text2image_prompt, img_file)


def generate_img_file(desc, img_file):
    from dashscope.common.error import InvalidTask
    dashscope.api_key = os.environ.get("DASHSCOPE_API_KEY")
    assert dashscope.api_key

    prompt = desc
    try:
        print("正在进行图片生成，请稍后。。。")
        rsp = dashscope.ImageSynthesis.call(
            model='wanx-v1',
            prompt=prompt,
            n=1,
            size='1024*1024')
        print("正在写入图片。。。")
        # save file to current directory
        if rsp.status_code == HTTPStatus.OK:
            for result in rsp.output.results:
                with open(img_file, 'wb+') as f:
                    f.write(requests.get(result.url).content)
                    img = Image.open(img_file)
                    img.show()
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))
    except InvalidTask as e:
        print(e)


def format_cover_html():
    image_src = covert_image_to_base64('assets/logo.png')
    return f"""
<div class="bot_cover">
    <div class="bot_avatar">
        <img src={image_src} alt="产品大师logo">
    </div>
    <div class="bot_name">{"由专业大模型助手收集客户需求，完成产品设计"}</div>
    <div class="bot_desp">{"这是一款由大模型驱动的产品设计大师，快来体验吧😊"}</div>
</div>
"""


def format_desc_html():
    return f"""
<div class="bot_cover">
    <div class="bot_rule">{"游戏介绍"}</div>
    <div class="bot_desp">{"游戏中包含的角色主要有："}
        <ul>
            <li>主持人Agent：每轮游戏开始会从中国古典诗词常见意象的关键字中随机选择出题</li>
            <li>评审官Agent：根据主持人提供的关键字和用户提供的诗句，判断是否回答正确，评审规则是：1.必须来自中国古诗词；2.必须包含主持人提供的关键字；3.不能和之前的诗句重复。</li>
            <li>对手Agent：和用户对垒，必须确保回答来自中国古诗词，且不能和之前重复</li>
        </ul>
    </div>
"""


def format_welcome_html():
    config = {
        'name': "Agent辅助产品设计",
        'description': '这是一款由多个大模型Agent驱动的产品设计大师，快来体验吧😊',
        'introduction_label': "<br>角色介绍",
        'rule_label': "<br>规则介绍",
        'char1': '销售导购Agent：富有经验的产品销售，通过问卷形式收集客户对于产品风格，产品颜色，产品外观，产品功能方面的需求',
        'char2': '助理Agent：总结助理先根据问答总结客户对产品的需求，包括功能性需求，外观性需求，价格需求等信息；然后交由信息提取助理提取关键产品特征，交给设计师',
        'char3': '设计师Agent：把产品特征翻译为英文，通过调用大模型文本生图能力，生成产品原型图',
        'char4': '产品经理Agent：在完成原型设计以后，和客户进行产品方面的答疑和沟通',
        'rule1': '1.客户只有2个环节需要沟通：销售导购沟通环节和产品经理沟通环节',
        'rule2': '2.回答为exit和空则退出当前问答，由产品设计师出图（如果没有收集到需求，则缺省将为地中海白色风格）',
        'rule3': '3.在沟通后客户可以进行答案的修正，在和产品经理沟通过程中，可以通过‘开始’或者‘重新’关键词返回销售导购的环节',

    }
    image_src = covert_image_to_base64('assets/logo.png')
    return f"""
<div class="bot_cover">
    <div class="bot_avatar">
        <img src={image_src} />
    </div>
    <div class="bot_name">{config.get("name")}</div>
    <div class="bot_desc">{config.get("description")}</div>
    <div class="bot_intro_label">{config.get("introduction_label")}</div>
    <div class="bot_intro_ctx">
        <ul>
            <li>{config.get("char1")}</li>
            <li>{config.get("char2")}</li>
            <li>{config.get("char3")}</li>
            <li>{config.get("char4")}</li>
        </ul>
    </div>
    <div class="bot_intro_label">{config.get("rule_label")}</div>
    <div class="bot_intro_ctx">
        <ul>
            <li>{config.get("rule1")}</li>
            <li>{config.get("rule2")}</li>
            <li>{config.get("rule3")}</li>
        </ul>
    </div>
</div>
"""
