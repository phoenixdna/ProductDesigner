import os
import json
import gradio as gr
from gradio.components import Chatbot
import threading
import agentscope
from agentscope.agents import DialogAgent
from agentscope.agents.user_agent import UserAgent
from agentscope.message import Msg
from utils import format_cover_html, format_desc_html



uid = threading.current_thread().name
host_avatar = 'assets/host_image.png'
user_avatar = 'assets/user_image.png'

def init_user(state):
    model_configs = json.load(open('configs/model_configs.json', 'r'))
    model_configs[0]["api_key"] = os.environ.get("DASHSCOPE_API_KEY")
    agents = agentscope.init(
        model_configs=model_configs,
        agent_configs="configs/agent_configs_poem.json",
    )
    host_agent = agents[0]
    judge_agent = agents[1]
    parti_agent = agents[2]
    # user_agent = UserAgent()
    
    # state['user_agent'] = user_agent
    state['host_agent'] = host_agent
    state['judge_agent'] = judge_agent
    state['parti_agent'] = parti_agent
    return state

# 创建 Gradio 界面
customTheme = gr.themes.Default(primary_hue=gr.themes.utils.colors.blue, radius_size=gr.themes.utils.sizes.radius_none)

demo = gr.Blocks(css='assets/appBot.css', theme=customTheme)
with demo:
    warning_html_code = """
        <div class="hint" style="background-color: rgba(255, 255, 0, 0.15); padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ffcc00;">
            <p>🌟\N{fire} Powered by <a href="https://github.com/modelscope/agentscope">AgentScope</a></p>
        </div>
        """
    gr.HTML(warning_html_code)
    state = gr.State({'session_seed': uid})
    with gr.Row(elem_classes='container'):
        with gr.Column(scale=4):
            with gr.Column():
                user_chatbot = Chatbot(
                    value=[[None, '您好，欢迎来到 飞花令大挑战，如果你准备好了，请回答「开始」']],
                    elem_id='user_chatbot',
                    # elem_classes=['markdown-body'],
                    avatar_images=[user_avatar, host_avatar],
                    height=600,
                    latex_delimiters=[],
                    show_label=False)
            with gr.Row():
                with gr.Column(scale=12):
                    preview_chat_input = gr.Textbox(
                        show_label=False,
                        container=False,
                        placeholder='尽情挥洒你的才情吧')
                with gr.Column(min_width=70, scale=1):
                    preview_send_button = gr.Button('发送', variant='primary')

        with gr.Column(scale=1):
            user_chat_bot_cover = gr.HTML(format_cover_html())
            user_chat_bot_desc = gr.HTML(format_desc_html())
            
    def send_message(chatbot, input, _state):
        # 将发送的消息添加到聊天历史
        # user_agent = _state['user_agent']
        host_agent = _state['host_agent']
        judge_agent = _state['judge_agent']
        parti_agent = _state['parti_agent']
        
        chatbot.append((input, ''))
        yield {
            user_chatbot: chatbot,
            preview_chat_input: '',
        }
        if '开始' in input:
            # 开始处理
            msg = Msg(name="system", content="飞花令游戏规则：请回答一句包含特定关键字的中国古诗词。下面有请主持人出题。")
            chatbot[-1] = (input, f'{msg.content}')
            yield {
                user_chatbot: chatbot,
            }
            host_msg = host_agent(msg)
            chatbot.append((None, f"主持人：本轮的关键字是：{host_msg.content}"))
            yield {
                user_chatbot: chatbot,
            }
            global pre_host_key
            pre_host_key = host_msg.content
        else:
            judge_content = f'主持人的关键字是{pre_host_key}，用户的诗句是{input}'
            judge_msg = judge_agent(Msg(name='judge', content=judge_content))
            chatbot[-1] = (input, f'评审官：{judge_msg.content}')
            yield {
                user_chatbot: chatbot,
            }
            if '结束' not in judge_msg.content:
                parti_content = f'主持人的关键字是{pre_host_key}'
                parti_msg = parti_agent(Msg(name='parti', content=parti_content))
                chatbot.append((None, f'对手答题：{parti_msg.content} 现在请选手继续答题'))
                yield {
                    user_chatbot: chatbot,
                }
            else:
                judge_msg = judge_agent(Msg(name='judge', content='本轮游戏结束，请将选手得分score重新初始化为5'))
                chatbot.append((None, '恭喜你完成挑战，如您想重新游戏，请回答「开始」'))
                yield {
                    user_chatbot: chatbot,
                }


    preview_send_button.click(
        send_message,
        inputs=[user_chatbot, preview_chat_input, state],
        outputs=[user_chatbot, preview_chat_input])
    preview_chat_input.submit(send_message,
        inputs=[user_chatbot, preview_chat_input, state],
        outputs=[user_chatbot, preview_chat_input])

    demo.load(init_user, inputs=[state], outputs=[state])

demo.queue()
demo.launch(share=True)
