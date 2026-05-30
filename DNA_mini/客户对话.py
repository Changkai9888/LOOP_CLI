from unifiedAPI import *
import json
import os
from datetime import datetime
if __name__ == "__main__":
    """主对话程序：连续对话并记录完整日志"""
    # 创建对话日志文件夹
    log_dir = "对话日志"
    os.makedirs(log_dir, exist_ok=True)
    # 每次启动时新建带时间戳的日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamp_file = os.path.join(log_dir, f"_dialog_{timestamp}.json")
    latest_file = os.path.join(log_dir, "_latest.json")
    # 初始化日志结构
    dialog_log = {
        "start_time": datetime.now().isoformat(),
        "conversations": []
    }
    print(f"AI对话系统已启动")
    print(f"时间戳日志: {timestamp_file}")
    print(f"最新日志: {latest_file}")
    print("输入 'exit' 或 'quit' 结束对话\n")
    dialogue_history = ""
    if os.path.isfile(log_dir+'/dialogue_history.txt'):
        re=input('是否恢复上次的对话记录？(y/n)')
        if re in ['y','Y','YES','yes','Yes']:
            with open(log_dir+'/dialogue_history.txt', 'r', encoding='utf-8') as f: dialogue_history = f.read()
    while True:
        # 获取用户输入
        user_input=input("\n[用户]: ")
        if user_input=='/':
            print("刷新")
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
        system_prompt = f"以下是本次对话历史信息：\n{dialogue_history}" if dialogue_history else None
        response = call_api(user_input, system_prompt=system_prompt)
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
        dialogue_history += f"\n用户({user_entry['timestamp']}): {user_input}"
        dialogue_history += f"\nAI({ai_entry['timestamp']}): {ai_entry['content']}"
        dialogue_history = dialogue_history[-int(1e5):] if len(dialogue_history) > int(1e5) else dialogue_history
        # 添加完整对话回合到日志
        conversation_round = {
            "user": user_entry,
            "assistant": ai_entry,
            "prompts": {  # 新增：记录提示词
                "user_prompt": user_prompt,  # 最终传给API的用户提示词
                "system_prompt": system_prompt     # 系统提示词
                        }
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
        with open(log_dir+"/dialogue_history.txt", "w", encoding="utf-8") as f:
            f.write(dialogue_history)

    # 最终保存
    dialog_log["end_time"] = datetime.now().isoformat()
    with open(timestamp_file, 'w', encoding='utf-8') as f:
        json.dump(dialog_log, f, ensure_ascii=False, indent=2)
    with open(latest_file, 'w', encoding='utf-8') as f:
        json.dump(dialog_log, f, ensure_ascii=False, indent=2)
    
    print(f"日志已保存到: {timestamp_file}")
    print(f"最新日志已更新: {latest_file}")
    with open(log_dir+"/dialogue_history.txt", "w", encoding="utf-8") as f:
        f.write(dialogue_history)

