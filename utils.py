import base64
from http import HTTPStatus
import requests

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


def format_cover_html():
    image_src = covert_image_to_base64('assets/logo.png')
    return f"""
<div class="bot_cover">
    <div class="bot_avatar">
        <img src={image_src} alt="飞花令logo">
    </div>
    <div class="bot_name">{"和Agent玩飞花令"}</div>
    <div class="bot_desp">{"这是一款由大模型驱动的中国古诗词-飞花令游戏，快来体验吧😊"}</div>
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
        'name': "和Agent玩飞花令",
        'description': '这是一款由多个大模型Agent驱动的中国古诗词-飞花令游戏，快来体验吧😊',
        'introduction_label': "<br>角色介绍",
        'rule_label': "<br>规则介绍",
        'char1': '主持人Agent：每轮游戏开始会从中国古典诗词常见意象的关键字中随机选择出题',
        'char2': '评审官Agent：根据主持人提供的关键字和用户提供的诗句，判断是否回答正确',
        'char3': '对手Agent：和用户对垒，确保回答来自中国古诗词且包含关键字，不能和之前重复',
        'rule1': '1.必须来自中国古诗词；',
        'rule2': '2.必须包含主持人提供的关键字；',
        'rule3': '3.不能和之前的诗句重复。',
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
