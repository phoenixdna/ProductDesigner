import os
import json
import gradio as gr
from gradio.components import Chatbot
import threading
import agentscope
from agentscope.agents import DialogAgent
from agentscope.agents.user_agent import UserAgent
from agentscope.message import Msg
from utils import format_welcome_html
import utils
from dotenv import find_dotenv, load_dotenv
_ = load_dotenv(find_dotenv()) 

uid = threading.current_thread().name
tutor_avatar = 'assets/tutor.png'
summarize_avatar = 'assets/summarize.png'
extract_avatar = 'assets/extract.png'
design_avatar = 'assets/design.png'
painter_avatar = 'assets/painter.png'
product_avatar = 'assets/product.png'
user_avatar = 'assets/user.png'

requirement = 'default'

i = 0

j = 0

history = ''

tutor = True

b_pic = False


def init_game(state):
    model_configs = json.load(open('configs/model_configs.json', 'r'))
    model_configs[0]["api_key"] = os.environ.get("DASHSCOPE_API_KEY")
    model_configs[1]["api_key"] = os.environ.get("DASHSCOPE_API_KEY")
    agents = agentscope.init(
        model_configs=model_configs,
        agent_configs="configs/agent_configs_poem.json",
    )
    user_agent = UserAgent()
    state['tutor_agent'] = agents[0]
    state['summarize_agent'] = agents[1]
    state['extract_agent'] = agents[2]
    state['design_agent'] = agents[3]
    state['painter'] = agents[4]
    state['product_agent'] = agents[5]
    return state

# 创建 Gradio 界面
demo = gr.Blocks(css='assets/appBot.css')
with demo:
    warning_html_code = """
        <div class="hint" style="background-color: rgba(255, 255, 0, 0.15); padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ffcc00;">
            <p>\N{fire} Powered by <a href="https://github.com/modelscope/agentscope">AgentScope</a></p>
        </div>
        """
    gr.HTML(warning_html_code)
    
    state = gr.State({'session_seed': uid})
    tabs = gr.Tabs(visible=True)
    with tabs:
        welcome_tab = gr.Tab('软件介绍', id=0)
        with welcome_tab:
            user_chat_bot_cover = gr.HTML(format_welcome_html())
        with gr.Row():
            new_button = gr.Button(value='🚀开始设计', variant='primary')
    
    game_tabs = gr.Tabs(visible=False)
    with game_tabs:
        main_tab = gr.Tab('主界面', id=0)
        with main_tab:
            with gr.Row():
                with gr.Column(min_width=270):
                    user_chatbot = gr.Chatbot(
                        elem_classes="app-chatbot",
                        avatar_images=[summarize_avatar, extract_avatar,product_avatar],
                        label="记录和提示区",
                        show_label=True,
                        bubble_full_width=False,
                    )
                with gr.Column(min_width=270):
                    user_chatsys = gr.Chatbot(
                        value=[['您好，欢迎来到 产品设计大师，先由我们专业的销售导购和您交流您的需求，你只需要做出简单选择即可，输入任意字符开始', None]],
                        elem_classes="app-chatbot",
                        avatar_images=[user_avatar, tutor_avatar, painter_avatar],
                        label="系统栏",
                        show_label=True,
                        bubble_full_width=False,
                    )
            with gr.Row():
                with gr.Column(scale=12):
                    user_chat_input = gr.Textbox(
                        label='user_chat_input',
                        show_label=False,
                        placeholder='尽情挥洒你的才情吧')
                with gr.Column(min_width=70, scale=1):
                    send_button = gr.Button('📣发送', variant='primary')
            with gr.Row():
                return_welcome_button = gr.Button(value="↩️返回首页")
            with gr.Row():
                image_preview = gr.Image('assets/logo.png', width=300)  # 设置图片路径和宽度
    
    def game_ui():
        return {tabs: gr.update(visible=False), game_tabs: gr.update(visible=True)}

    def welcome_ui():
        return {tabs: gr.update(visible=True), game_tabs: gr.update(visible=False)}






    def send_message(chatbot, chatsys, user_input, _state):
        # 将发送的消息添加到聊天历史
        global tutor
        global history
        global i
        global j
        tutor_agent = _state['tutor_agent']
        summarize_agent = _state['summarize_agent']
        extract_agent = _state['extract_agent']
        design_agent = _state['design_agent']
        painter = _state['painter']
        product_agent = _state['product_agent']
        chatsys.append((user_input, None))
        yield {
            user_chatbot: chatbot,
            user_chatsys: chatsys,
            user_chat_input: '',
        }
        if tutor:
            if 'exit' in user_input or len(user_input) == 0:
                tutor = False
                if i > 1:
                    print("here is the summarize part")
                    chatbot.append(("下面由总结助手进行总结，请稍后。。。", None))
                    yield {
                        user_chatbot: chatbot,
                        user_chatsys: chatsys,
                    }
                    summarize_msg = summarize_agent(history)
                    chatbot.append((f"{summarize_msg.content}", None))
                    yield {
                        user_chatbot: chatbot,
                        user_chatsys: chatsys,
                    }
                    print("here is the extract part")
                    chatbot.append(("进行关键词抽取，请稍后。。。", None))
                    yield {
                        user_chatbot: chatbot,
                        user_chatsys: chatsys,
                    }
                    extract_msg = extract_agent(summarize_msg)
                    chatbot.append((f"{extract_msg.content}", None))
                    yield {
                        user_chatbot: chatbot,
                        user_chatsys: chatsys,
                    }
                    requirement = extract_msg.content
                else:
                    print("using default")

                    requirement = "白色，地中海风格"
                    chatbot.append((f"""下面使用缺省样式：{requirement}进行设计。。。""", None))
                    yield {
                        user_chatbot: chatbot,
                        user_chatsys: chatsys,
                    }

                print("here is the prompt part")

                msg = Msg(
                    name="user",
                    role="user",
                    content="儿童学习桌椅，" + requirement
                )
                chatbot.append(("生成英文提示词。。。", None))
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
                design_msg = design_agent(msg)
                chatbot.append((f"{design_msg.content}", None))
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
                chatbot.append(("下面设计师根据您的需求进行图片生成，耗时较长，请您耐心等候。。。", None))
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
                xx = painter(design_msg)
                image_url = xx.url[0]
                #                xmsg = Msg(
                #                    name="user",
                #                    role="user",
                #                    content=xx.content,
                #                    url=xx.url,
                #                )
                #                chatbot.append((f"""生成的图片如下\n\n<img src="{image_url}" alt="{image_url}" />""", None))

                chatbot.append((f"""生成的图片如下：\n
                            <a href="{image_url}">
                              <img src="{image_url}" alt="{image_url}">
                            </a>
                            """, None))
                # f"""<img src="{image_url}"></img>"""
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
            else:
                tutor_msg = tutor_agent(user_input)
                #tutor_msg.role = "assistant"
                history = history + tutor_msg.content
                chatsys.append((f"{tutor_msg.content}", None))
                i = i+1
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
        else:
            if 'exit' in user_input or len(user_input) == 0:
                print("here is the finish part")
                chatsys.append(("谢谢您的使用，有任何建议请联系：nasonw@163.com", None))
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }

            else:
                j = j+1
                if j > 1:

                    product_msg = product_agent(user_input)
                    chatsys.append((f"{product_msg.content}", None))
                    yield {
                        user_chatbot: chatbot,
                        user_chatsys: chatsys,
                    }
                else:
                    chatsys.append(("下面由我们的产品经理为您服务和答疑", None))
                    yield {
                        user_chatbot: chatbot,
                        user_chatsys: chatsys,
                    }





    # change ui
    new_button.click(game_ui, outputs=[tabs, game_tabs])
    return_welcome_button.click(welcome_ui, outputs=[tabs, game_tabs])

    # submit message
    send_button.click(
        send_message,
        inputs=[user_chatbot, user_chatsys, user_chat_input, state],
        outputs=[user_chatbot, user_chatsys, user_chat_input]
    )
    user_chat_input.submit(
        send_message,
        inputs=[user_chatbot, user_chatsys, user_chat_input, state],
        outputs=[user_chatbot, user_chatsys, user_chat_input]
    )
    demo.load(init_game, inputs=[state], outputs=[state])

demo.queue()
demo.launch(share=True)
