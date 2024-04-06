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
from dotenv import find_dotenv, load_dotenv
_ = load_dotenv(find_dotenv()) 

uid = threading.current_thread().name
tutor_avatar = 'assets/tutor.png'
summarize_avatar = 'assets/summarize.png'
extract_avatar = 'assets/extract.png'
design_avatar = 'assets/design.png'
user_avatar = 'assets/user.png'


def init_game(state):
    model_configs = json.load(open('configs/model_configs.json', 'r'))
    model_configs[0]["api_key"] = os.environ.get("DASHSCOPE_API_KEY")
    agents = agentscope.init(
        model_configs=model_configs,
        agent_configs="configs/agent_configs_poem.json",
    )
    user_agent = UserAgent()
    state['tutor_agent'] = agents[0]
    state['summarize_agent'] = agents[1]
    state['extract_agent'] = agents[2]
    state['design_agent'] = agents[3]
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
        welcome_tab = gr.Tab('游戏介绍', id=0)
        with welcome_tab:
            user_chat_bot_cover = gr.HTML(format_welcome_html())
        with gr.Row():
            new_button = gr.Button(value='🚀开始挑战', variant='primary')
    
    game_tabs = gr.Tabs(visible=False)
    with game_tabs:
        main_tab = gr.Tab('主界面', id=0)
        with main_tab:
            with gr.Row():
                with gr.Column(min_width=270):
                    user_chatbot = gr.Chatbot(
                        elem_classes="app-chatbot",
                        avatar_images=[user_avatar, tutor_avatar],
                        label="记录和提示区",
                        show_label=True,
                        bubble_full_width=False,
                    )
                with gr.Column(min_width=270):
                    user_chatsys = gr.Chatbot(
                        value=[['您好，欢迎来到 产品大师，如果你准备好了，请输入「开始」', None]],
                        elem_classes="app-chatbot",
                        avatar_images=[summarize_avatar, extract_avatar],
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
        tutor_agent = _state['tutor_agent']
        summarize_agent = _state['summarize_agent']
        extract_agent = _state['extract_agent']
        design_agent = _state['design_agent']
        chatbot.append((user_input, None))
        yield {
            user_chatbot: chatbot,
            user_chatsys: chatsys,
            user_chat_input: '',
        }
        global userinfo 
        userinfo = 'default'
        if '开始' in user_input:
            msg = Msg(name="system", content="下面我们的销售经理将会向你提问了解您对产品的需求，目前产品类别是儿童桌椅")
            chatsys.append((f'{msg.content}', None))
            yield {
                user_chatbot: chatbot,
                user_chatsys: chatsys,
            }
            tutor_msg = tutor_agent(msg)
            chatsys.append((f"{tutor_msg.content}", None))
            yield {
                user_chatbot: chatbot,
                user_chatsys: chatsys,
            }
            
            while user_input!='Exit' or user_input!='':
                user_agent = UserAgent(name='user', content=user_input)
                chatsys.append((user_input, None))
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
                tutor_msg = tutor_agent(user_agent)
                chatsys.append((f"{tutor_msg.content}", None))
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
        else:
            msg = Msg(name="sytem", content=f"用户输入是{userinfo}")
            if userinfo != 'default':
                summarize_msg = summarize_agent(Msg(name='summarize', content=chatsys.content))
                chatbot.append((None, f'总结助手：{summarize_msg.content}'))
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
                extract_msg = extract_agent(Msg(name='extract', content=chatsys.content))
                chatbot.append((None, f'提取助手：{extract_msg.content}'))
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
                userinfo = extract_msg.content
        utils.createimg(userinfo)
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
