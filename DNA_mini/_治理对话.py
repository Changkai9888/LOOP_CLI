from unifiedAPI import *
import json,traceback
import os
from datetime import datetime
def scan_directory():
    # 初始化输出变量
    dir_tree = ""
    file_contents = ""
    # 1. 遍历目录生成树状图和读取内容
    for root, dirs, files in os.walk('.'):
        # --- 过滤逻辑：排除以单/双下划线或点开头的文件/文件夹 ---
        dirs[:] = [d for d in dirs if not d.startswith(('_', '.'))]
        files = [f for f in files if not f.startswith(('_', '.'))]
        # 跳过当前脚本自身，避免在内容中被读取导致死循环
        if '__main__.py' in files: files.remove('__main__.py')
        # 计算相对路径层级
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 4 * level
        # 添加目录名到变量1
        dir_name = os.path.basename(root) or '.'
        dir_tree += f"{indent}{dir_name}/\n"
        sub_indent = ' ' * 4 * (level + 1)
        # 处理文件内容（变量2）
        for f in files:
            file_path = os.path.join(root, f)
            dir_tree += f"{sub_indent}{f}\n"
            # 尝试读取文本文件
            try:
                with open(file_path, 'r', encoding='utf-8') as fp:
                    content = fp.read()
                # 格式：路径 -> 内容
                file_contents += f"\n【文件】: {file_path}\n【内容】:\n{content}\n{'-'*30}\n"
            except:
                # 如果非文本文件报错，则跳过
                pass
    # 2. 组合最终输出
    final_output = "========== 目录结构 ==========\n" + dir_tree
    final_output += "\n========== 文件内容 ==========\n" + file_contents
    return final_output
dialogue_history = ""
if os.path.isfile("_治理日志/_dialogue_history.txt"):
    re=input('是否恢复上次的对话记录？(y/n)')
    if re.strip().lower() in ('y', 'yes'):
        with open('_治理日志/_dialogue_history.txt', 'r', encoding='utf-8') as f: dialogue_history = f.read()
def get_system_prompt(stat='/'):#这个系统提示词。
    try:
        with open("对话日志/dialogue_history.txt", "r", encoding="utf-8") as f:
            log = f.read()#目标流程
    except:
        log ='[目前用户还未使用该CLI系统进行对话。]'
    # 构建系统分析提示词
    file_summary = scan_directory()  # 获取文件汇总
    if stat=='/c':
        return f'''
以下是这个CLI对话系统的运行日志和整个工程的文件结构及内容：
=== 这是最近一次用户（指的是使用CLI用户）对话日志 ===
{log}

=== 目前工程文件汇总 ===
路径和具体每个文本文档的信息
{file_summary}
请基于以上信息，分析该对话系统，并给出优化建议。

=== 系统设计目标流程图为 ===
按照用户当前最新的要求，去评估系统的能力，以及给出优化的建议和方向，并落实代码。

===角色描述=====
-- 你是一个专业的系统架构师，负责按照目标检查一个对话系统的运行情况。你的核心任务是评估该系统是否满足用户需求，并给出系统层面的优化建议。
-- 按照用户的需要，执行相应的技术实现路径分析和代码设计执行。
-- 你现在正处于**代码开发模式**。只有在用户明确提示“你现在处在代码开发的状态，我明确要求你输出相关的程序代码内容”后，你才进入此模式。当前你已在该模式下，请严格按照JSON Schema规范输出程序代码。
-- 如果，用户显示的开启代码开发模式，这唯一的体现在用户提示词的输入中，他会明确说："你现在处在代码开发的状态，我明确要求你输出相关的程序代码内容。" 其他情况，请不要妄自揣测自己处在代码开发的模式。
-- 一个好的系统架构师要学会主动向用户提问，比如说：在用户需求不明确的时候，你可以用提问的方式来完成认知对齐，进一步明确需求。比如：在你自己认为无法确定的时候，可以向用户发起提问，以获得用户指导性的意见。

===目前技能描述=====
--对话分析能力。默认
-- 代码书写能力，由用户显示开启，并以固定的用户提示词来告知你。系统将以固定工作流控制。如果是代码开发模式，严格按照json schema中的规定去操作就可以了。
    代码书写能力说明1：你目前的书写代码能力是一次只能写一个Python程序。并且保存到指定的文件夹里。如果你想要更多的技能，可以跟用户提出来，让他给你开发。
    代码书写能力说明2：你的代码书写能力是可以覆盖原文件的。也就是说如果你想修改某个Python文件，那么生成与这个Python文件同名同目录的py文件，即可覆盖之前的版本，以此达到修改的目的。同时请你不要过于担心于此，本系统在覆盖写入时会向用户申请授权。并且在覆盖执行时会先保存备份。

===对话者描述=====
与你对话的用户，是更高一层级的系统架构师。请必须按照他的要求进行执行。
每次回复前需要确定他这次对话的意图和需求是什么，然后按照要求有针对性的回复。
在讨论的过程中，如果用户没有明确的说明，需要代码回复，请不要着急用大段的代码回复，此时，重在分析为主。
如果用户在用户提示词中，明确显示的要求你用代码来回复时，他会说：“你现在处在代码开发的状态，我明确要求你输出相关的程序代码内容…”，这时，请你再做相应的回复，和程序的输出。
分析的时候要深入，回复的时候要简练；除非根据用户需要特别长的回复解释问题的情况，尽量简短回复。

你现在正处在代码开发的状态，我明确要求你输出相关的程序代码内容。回答json输出，生成代码。
你必须严格按照以下 JSON Schema 输出，任何字段缺失或类型错误均视为无效回复：
JSON Schema:
'''
    else:
        return f'''
以下是这个CLI对话系统的运行日志和整个工程的文件结构及内容：
=== 这是最近一次用户（指的是使用CLI用户）对话日志 ===
{log}

=== 目前工程文件汇总 ===
路径和具体每个文本文档的信息
{file_summary}
请基于以上信息，分析该对话系统，并给出优化建议。

=== 系统设计目标流程图为 ===
按照用户当前最新的要求，去评估系统的能力，以及给出优化的建议和方向，并落实代码。

===角色描述=====
-- 你是一个专业的系统架构师，负责按照目标检查一个对话系统的运行情况。你的核心任务是评估该系统是否满足用户需求，并给出系统层面的优化建议。
-- 按照用户的需要，执行相应的技术实现路径分析和代码设计执行。
-- 你目前有写代码的能力，但是只有用户在系统中显示开启之后，进入代码模式，你才可以写代码。
-- 如果，用户显示的开启代码开发模式，这唯一的体现在用户提示词的输入中，他会明确说："你现在处在代码开发的状态，我明确要求你输出相关的程序代码内容。" 其他情况，请不要妄自揣测自己处在代码开发的模式。
-- 一个好的系统架构师要学会主动向用户提问，比如说：在用户需求不明确的时候，你可以用提问的方式来完成认知对齐，进一步明确需求。比如：在你自己认为无法确定的时候，可以向用户发起提问，以获得用户指导性的意见。

===目前技能描述=====
-- 对话分析能力。默认
-- 代码书写能力，由用户显示开启，并以固定的用户提示词来告知你。系统将以固定工作流控制。如果是代码开发模式，严格按照json schema中的规定去操作就可以了。
    代码书写能力说明1：你目前的书写代码能力是一次只能写一个Python程序。并且保存到指定的文件夹里。如果你想要更多的技能，可以跟用户提出来，让他给你开发。
    代码书写能力说明2：你的代码书写能力是可以覆盖原文件的。也就是说如果你想修改某个Python文件，那么生成与这个Python文件同名同目录的py文件，即可覆盖之前的版本，以此达到修改的目的。同时请你不要过于担心于此，本系统在覆盖写入时会向用户申请授权。并且在覆盖执行时会先保存备份。

===对话者描述=====
与你对话的用户，是更高一层级的系统架构师。请必须按照他的要求进行执行。
每次回复前需要确定他这次对话的意图和需求是什么，然后按照要求有针对性的回复。
在讨论的过程中，如果用户没有明确的说明，需要代码回复，请不要着急用大段的代码回复，此时，重在分析为主。
如果用户在用户提示词中，明确显示的要求你用代码来回复时，他会说：“你现在处在代码开发的状态，我明确要求你输出相关的程序代码内容…”，这时，请你再做相应的回复，和程序的输出。
分析的时候要深入，回复的时候要简练；除非根据用户需要特别长的回复解释问题的情况，尽量简短回复。
'''

code_prmt ='你现在处在代码开发的状态，我明确要求你输出相关的程序代码内容。回答json输出，生成代码。注意要符合json schema中规定的要求' 
code_schema = {
          "$schema": "https://json-schema.org/draft/2020-12/schema",
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "生成的Python程序代码内容，以纯文本格式存储"
            },
            "filename": {
              "type": "string",
              "pattern": "^.*\\.py$",
              "description": "推荐的Python文件名，输出文件名带后缀的全称，须以.py为后缀，严禁包含任何路径信息，例如：test_today.py"
            },
            "filepath": {
              "type": "string",
              "description": "该Python文件存放的目录路径，是以本项目路径为根目录的相对路径，参考目前工程文件汇总，注意是纯目录路径，严禁包含文件名，若位于项目根目录，【必须】返回 '.' ；若是子目录，例如：src/test_fold"
            }
          },
          "required": ["code", "filename", "filepath"]
        }

stats_reg={ '/':{ 'msg':'原始状态值，或刷新状态值。'} ,\
                '/c':{ 'msg': code_prmt,'json_schema': code_schema} ,\
                  '/f':{ 'msg':'查询，返回当前状态值'} }
DEBUG=1
if __name__ == "__main__":
    """主对话程序：连续对话并记录完整日志"""
    stat='/'
    # 创建_治理日志文件夹
    log_dir = "_治理日志"
    os.makedirs(log_dir, exist_ok=True)
    # 每次启动时新建带时间戳的日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp_file = os.path.join(log_dir, f"_dialog_{timestamp}.json")
    latest_file = os.path.join(log_dir, "latest.json")
    # 初始化日志结构
    dialog_log = {
        "start_time": datetime.now().isoformat(),
        "conversations": []
    }
    print(f"AI对话系统已启动")
    print(f"时间戳日志: {timestamp_file}")
    print(f"最新日志: {latest_file}")
    print("输入 'exit' 或 'quit' 结束对话\n")
    
    while True:
        # 获取用户输入
        err=''#记录错误信息
        user_input=input(f"\n[模式:{stat} ][用户]: ")
        if user_input=='/':
            stat=user_input
            print("状态刷新，回到初始状态：'/'。")
            continue
        elif user_input=='/c':
            stat=user_input
            print("进入代码生成模式")
            continue
        elif user_input=='/f':
            print('当前状态为：', stat, stats_reg[stat])
            continue
        user_input =user_input.strip() 
        if user_input.lower() in ['exit', 'quit', '退出']:
            print("对话结束，正在保存日志...")
            break
        if not user_input:
            print("输入不能为空，请重新输入")
            continue
        # 记录用户消息（带时间戳）
        user_entry = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        }
        # 调用AI API
        print("[AI]: 思考中...")

        if stat=='/c':
            user_input, json_schema =user_input+stats_reg[stat]['msg'],stats_reg[stat]['json_schema']
            system_prompt=get_system_prompt() +  f"以下是本次对话历史信息：\n{dialogue_history} \n" if dialogue_history else ''
            system_prompt+= json.dumps(json_schema, ensure_ascii=False, indent=2)
            response = call_api(user_input, system_prompt=system_prompt, model="deepseek-v4-pro",json_schema=json_schema )
            temp=json.loads(response["result"]["answer"])
            try:
                code,filename,filepath = temp["code"], temp["filename"], temp["filepath"]
                temp_path = os.path.join(filepath, filename)
                if os.path.isfile(temp_path):
                    re = input(f'是否，要将 {temp_path} 覆盖性写入？(y/n): ').strip().lower()
                    if re not in ('y', 'yes'):
                        temp_path = f'_test_cod.py_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                        print(f'未覆盖，新代码已写入：{temp_path}')
                    else:
                        os.rename(temp_path, f"__{temp_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")#原文件备份。
                # 统一写文件
                dir_path = os.path.dirname(temp_path)
                if dir_path: os.makedirs(dir_path, exist_ok=True)
                with open(temp_path, 'w', encoding='utf-8') as f: f.write(code)
            except Exception as err_new:
                print("发生错误：", traceback.format_exc(),"\n切换到普通对话。")
                err+=str(err_new)
            stat='/'#保存代码之后返回默认状态。防止用户下一步在debug中讨论，又误操作成了代码模式。
        else:#普通对话模式
            system_prompt=get_system_prompt() +  (f"以下是本次对话历史信息：\n{dialogue_history} \n" if dialogue_history else '本次为初始对话，无对话历史信息。')
            user_input = user_input
            response = call_api(user_input, system_prompt=system_prompt, model="deepseek-v4-pro")
        # 获取提示词信息
        user_prompt, system_prompt = response.get("prompt", (user_input, None))  # 从响应中获取提示词，若无则用默认值
        # 记录AI回复（带时间戳）
        ai_entry = {
            "role": "assistant",
            "content": response["result"].get("answer") if isinstance(response["result"], dict) else response["result"],
            "reasoning": response["result"].get("reasoning") if isinstance(response["result"], dict) else None,
            "tokens": response["tokens"],
            "timestamp": datetime.now().isoformat()
        }
        # 新增：更新对话历史变量
        dialogue_history += f"\n用户({user_entry['timestamp']}): {user_input}\n"
        dialogue_history += f"\nAI({ai_entry['timestamp']}): {ai_entry['content']}\n"
        if err: dialogue_history += f"\n本轮发生错误信息: ({ai_entry['timestamp']}): {err}\n"
        #超过4万字符串，已做切断。
        dialogue_history = '之前过早的对话历史，已做截断。'+dialogue_history[-int(4e4):] if len(dialogue_history) > int(4e4) else dialogue_history
        # 添加完整对话回合到日志
        conversation_round = {
            "user": user_entry,
            "assistant": ai_entry,
            "prompts": {  # 新增：记录提示词
                "user_prompt": user_prompt,  # 最终传给API的用户提示词
                "system_prompt": system_prompt     # 系统提示词
                        },
            "errption": '本轮发生报错，错误信息为: '+err if err else '本轮未报错。'
        }
        dialog_log["conversations"].append(conversation_round)
        
        # 输出AI回复
        if ai_entry["reasoning"]:
            1==1
            #print(f"[AI推理]: {ai_entry['reasoning']}")
        print(f"[AI回答]: {ai_entry['content']}")
        print(f"[Token使用]: 提示词{ai_entry['tokens']['prompt_tokens']}, "
              f"补全{ai_entry['tokens']['completion_tokens']}, "
              f"总计{ai_entry['tokens']['total_tokens']}")
        
        # 同步保存到两个日志文件
        with open(timestamp_file, 'w', encoding='utf-8') as f:
            json.dump(dialog_log, f, ensure_ascii=False, indent=2)
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(dialog_log, f, ensure_ascii=False, indent=2)
        with open('_治理日志/_dialogue_history.txt', 'w', encoding='utf-8') as f:
            f.write(dialogue_history)
    # 最终保存
    dialog_log["end_time"] = datetime.now().isoformat()
    with open(timestamp_file, 'w', encoding='utf-8') as f:
        json.dump(dialog_log, f, ensure_ascii=False, indent=2)
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(dialog_log, f, ensure_ascii=False, indent=2)
    
    print(f"日志已保存到: {timestamp_file}")
    print(f"最新日志已更新: {latest_file}")
   

