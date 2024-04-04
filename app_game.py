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
host_avatar = 'assets/host_image.png'
user_avatar = 'assets/user_image.png'
judge_avatar = 'assets/judge_image.png'
parti_avatar = 'assets/parti_image.png'

def init_game(state):
    model_configs = json.load(open('configs/model_configs.json', 'r'))
    model_configs[0]["api_key"] = os.environ.get("DASHSCOPE_API_KEY")
    agents = agentscope.init(
        model_configs=model_configs,
        agent_configs="configs/agent_configs_poem.json",
    )
    state['host_agent'] = agents[0]
    state['judge_agent'] = agents[1]
    state['parti_agent'] = agents[2]
    return state

# 创建 Gradio 界面
demo = gr.Blocks(css='assets/app.css')
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
                        avatar_images=[user_avatar, parti_avatar],
                        label="答题区",
                        show_label=True,
                        bubble_full_width=False,
                    )
                with gr.Column(min_width=270):
                    user_chatsys = gr.Chatbot(
                        value=[['您好，欢迎来到 飞花令大挑战，如果你准备好了，请回答「开始」', None]],
                        elem_classes="app-chatbot",
                        avatar_images=[host_avatar, judge_avatar],
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
    
    def game_ui():
        return {tabs: gr.update(visible=False), game_tabs: gr.update(visible=True)}

    def welcome_ui():
        return {tabs: gr.update(visible=True), game_tabs: gr.update(visible=False)}

    def send_message(chatbot, chatsys, user_input, _state):
        # 将发送的消息添加到聊天历史
        host_agent = _state['host_agent']
        judge_agent = _state['judge_agent']
        parti_agent = _state['parti_agent']
        chatbot.append((user_input, None))
        yield {
            user_chatbot: chatbot,
            user_chatsys: chatsys,
            user_chat_input: '',
        }
        if '开始' in user_input:
            msg = Msg(name="system", content="飞花令游戏规则：请回答一句包含特定关键字的中国古诗词。下面有请主持人出题。")
            chatsys.append((f'{msg.content}', None))
            yield {
                user_chatbot: chatbot,
                user_chatsys: chatsys,
            }
            host_msg = host_agent(msg)
            chatsys.append((f"主持人：本轮的关键字是：{host_msg.content}", None))
            yield {
                user_chatbot: chatbot,
                user_chatsys: chatsys,
            }
            global pre_host_key
            pre_host_key = host_msg.content
        else:
            judge_content = f'主持人的关键字是{pre_host_key}，用户的诗句是{user_input}'
            judge_msg = judge_agent(Msg(name='judge', content=judge_content))
            chatsys.append((None, f'评审官：{judge_msg.content}'))
            yield {
                user_chatbot: chatbot,
                user_chatsys: chatsys,
            }
            if '结束' not in judge_msg.content:
                parti_content = f'主持人的关键字是{pre_host_key}'
                parti_msg = parti_agent(Msg(name='parti', content=parti_content))
                chatbot.append((None, f'对手答题：{parti_msg.content} 现在请选手继续答题。'))
                yield {
                    user_chatbot: chatbot,
                    user_chatsys: chatsys,
                }
            else:
                judge_msg = judge_agent(Msg(name='judge', content='本轮游戏结束，请将选手得分score重新初始化为5'))
                chatsys.append(('恭喜你完成挑战，如您想重新游戏，请回答「开始」', None))
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
