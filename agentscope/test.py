import agentscope
from agentscope.agents import DialogAgent
from agentscope.agents.user_agent import UserAgent
from agentscope.message import Msg
from agentscope.pipelines import SequentialPipeline

# agentscope.init(
#     model_configs={
#         "model_type": "dashscope_chat",
#         "config_name": "qwen",
#         "model_name": "qwen-max",
#         "api_key": "sk-3e99355c01a04a46ae3f3b8fcd67fe18",
#         "generate_args": {
#             "temperature": 0.5
#         }
#     }
# )

# 初始化了多个大模型
# agentscope.init(
#     model_configs="./model_configs.json"
# )
## 使用qwen大模型初始化一个对话agent
# dialog_agent_qwen = DialogAgent(
#     name="Assistant_qwen",
#     sys_prompt="You're a helpful assistant.",  # sys_prompt可以自行定义，不能为空
#     model_config_name="qwen",
# )
# msg = Msg(name = "贾维斯",content = "你好")
# print(msg)
# msg = dialog_agent_deepseek(msg)
# print(msg)
# msg = dialog_agent_qwen(msg)
# print(msg)


agents = agentscope.init(
    model_configs="./model_configs.json",  # 前面创建的model_configs.json文件
    agent_configs="./agent_configs_poem.json",
)

# 对应配置文件agent_configs.json中的顺序
# dialog_agent_qwen = agents[0]
# dialog_agent_deepseek = agents[1]
# 创建一个SequentialPipeline
# pipe = SequentialPipeline([dialog_agent_qwen, dialog_agent_deepseek])
# msg = Msg(name="Moderator", content="游戏规则：请回答一个四字中文成语，不要添加其他文字。请按规则接龙。本轮成语接龙起始词为「水落石出」")
# # 启动Pipeline
# pipe(msg) # 按顺序回答问题

host_agent = agents[0]
judge_agent = agents[1]
parti_agent = agents[2]
user_agent = UserAgent()
x = None
msg = Msg(name="system", content="飞花令游戏规则：请回答一句包含特定关键字的中国古诗词。下面有请主持人出题。")
host_msg = host_agent(msg)
while x is None or x.content != "退出":
    x = user_agent()
    judge_content = f'主持人的关键字是{host_msg.content}，用户的诗句是{x.content}'
    judge_msg = judge_agent(Msg(name='judge', content=judge_content))
    if '结束' in judge_msg.content:
        break
    parti_content = f'主持人的关键字是{host_msg.content}'
    parti_msg = parti_agent(Msg(name='parti', content=parti_content))

    




