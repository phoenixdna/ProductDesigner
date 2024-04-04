import time
import threading
import agentscope
from agentscope.agents import DialogAgent
from agentscope.agents.user_agent import UserAgent
from agentscope.message import Msg
from agentscope.pipelines import SequentialPipeline
from agentscope.web_ui.utils import send_chat_msg, generate_image_from_name

def main():
    agents = agentscope.init(
        model_configs="./model_configs.json",
        agent_configs="./agent_configs_poem.json",
    )

    host_agent = agents[0]
    judge_agent = agents[1]
    parti_agent = agents[2]
    user_agent = UserAgent()
    thread_name = threading.current_thread().name
    uid = thread_name

    x = None
    msg = Msg(name="system", content="飞花令游戏规则：请回答一句包含特定关键字的中国古诗词。下面有请主持人出题。")
    host_msg = host_agent(msg)
    host_avatar = generate_image_from_name(host_agent.name)
    judge_avatar = generate_image_from_name(judge_agent.name)
    parti_avatar = generate_image_from_name(parti_agent.name)
    send_chat_msg(f"您好，欢迎来到 飞花令大挑战，{msg.content}",
                      role=host_agent.name,
                      flushing=True,
                      uid=uid,
                      avatar=host_avatar)
    send_chat_msg(f"本轮的关键字是：{host_msg.content}",
                      role=host_agent.name,
                      flushing=True,
                      uid=uid,
                      avatar=host_avatar)
    while x is None or x.content != "退出":
        x = user_agent()
        judge_content = f'主持人的关键字是{host_msg.content}，用户的诗句是{x.content}'
        judge_msg = judge_agent(Msg(name='judge', content=judge_content))
        send_chat_msg(f"{judge_msg.content}",
                      role=judge_agent.name,
                      flushing=True,
                      uid=uid,
                      avatar=judge_avatar)
        time.sleep(0.5)
        if '结束' in judge_msg.content:
            break
        
        parti_content = f'主持人的关键字是{host_msg.content}'
        parti_msg = parti_agent(Msg(name='parti', content=parti_content))
        send_chat_msg(f"{parti_msg.content}",
                      role=parti_agent.name,
                      flushing=True,
                      uid=uid,
                      avatar=parti_avatar)

if __name__ == "__main__":
    main()




