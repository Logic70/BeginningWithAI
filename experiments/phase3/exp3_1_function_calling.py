"""
实验 3.1：Function Calling 基础
使用Ollama 实现工具调用
"""
import ollama
import json
import socket
import ipaddress
import subprocess

# 定义工具列表

tools = [
    {
        "type": "function",
        "function": {
            "name": "scan_port",
            "description": "扫描目标主机的指定端口是否开放",
            "parameters": {
                "type": "object",
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "目标主机IP或域名"
                    },
                    "port": {
                        "type": "integer",
                        "description": "要扫描的端口号"
                    }
                },
                "required": ["host", "port"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_vulnerability",
            "description": "检查目标是否存在指定漏洞",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "目标URL或IP"
                    },
                    "vuln_type": {
                        "type": "string",
                        "enum": ["sql_injection", "xss", "ssrf", "lfi"],
                        "description": "漏洞类型"
                    }
                },
                "required": ["target", "vuln_type"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"scan_ip",
            "description":"扫描目标网络所有存活的主机",
            "parameters":{
                "type":"object",
                "properties":{
                    "network":{
                        "type":"string",
                        "description":"目标网络IP段"
                    },
                    "mask":{
                        "type":"string",
                        "description":"子网掩码"
                    },
                    "timeout":{
                        "type":"integer",
                        "description":"超时时间,默认5秒"
                    }

                },
                "required":["network","mask"]
            }
        }
    }

]

def scan_port(host:str,port:int)->dict:
    """扫描指定主机的端口"""
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result=s.connect_ex((host,port))
            if result==0:
                return {"host":host,"port":port,"status":"open"}
            else:
                return {"host":host,"port":port,"status":"closed"}
    except Exception as e:
        return {"host":host,"port":port,"status":"error","message":str(e)}

def check_vulnerability(target:str,vuln_type:str)->dict:
    """检查目标是否存在指定漏洞"""
    try:
        if vuln_type=="sql_injection":
            return {"target":target,"vuln_type":vuln_type,"status":"open"}
        elif vuln_type=="xss":
            return {"target":target,"vuln_type":vuln_type,"status":"open"}
        elif vuln_type=="ssrf":
            return {"target":target,"vuln_type":vuln_type,"status":"open"}
        elif vuln_type=="lfi":
            return {"target":target,"vuln_type":vuln_type,"status":"open"}
    except Exception as e:
        return {"target":target,"vuln_type":vuln_type,"status":"error","message":str(e)}

def scan_ip(network:str,mask:str,timeout:int=1)->dict:
    """扫描目标网络所有存活的主机"""
    network_list=[]
    #解析IP段
    ip_list=ipaddress.ip_network(f"{network}/{mask}",strict=False)
    for ip in ip_list.hosts():
        network_list.append(str(ip))
    result_list = []
    #通过命令行ping扫描
    for ip in network_list:
        try:
            result=subprocess.run(["ping","-w",str(timeout),ip],capture_output=True,text=True)
            if result.returncode==0:
                result_list.append({"host":ip,"status":"open"})
            else:
                result_list.append({"host":ip,"status":"closed"})
        except Exception as e:
            result_list.append({"host":ip,"status":"error","message":str(e)})
    return result_list

# 工具映射
TOOL_MAP= {
    "scan_port":scan_port,
    "check_vulnerability":check_vulnerability,
    "scan_ip":scan_ip
}

def chat_with_tools(user_message:str,model:str = "qwen2.5:7b"):
    """与Ollama进行Function Calling对话

    Ollama SDK 的 ChatResponse 同时支持两种访问方式：
      - 属性访问: response.message.tool_calls
      - 字典访问: response["message"]["tool_calls"]
    本函数演示属性访问方式，两种方式等效。
    """
    messages=[{"role":"user","content":user_message}]

    # 第一次调用：让模型决定是否使用工具
    response = ollama.chat(
        model=model,
        messages=messages,
        tools=tools
    )

    # 检查是否有工具调用
    # 方式一（属性访问）: response.message.tool_calls
    # 方式二（字典访问）: response["message"].get("tool_calls")
    # 注意: tool_calls 在 response.message 下，不在 response 顶层！
    if response.message.tool_calls:
        for tool_call in response.message.tool_calls:
            # 方式一（属性）: tool_call.function.name / tool_call.function.arguments
            # 方式二（字典）: tool_call["function"]["name"] / tool_call["function"]["arguments"]
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments  # 已经是 dict，无需 json.loads

            print(f"\n🔧 调用工具: {func_name}")
            print(f"   参数: {json.dumps(func_args, ensure_ascii=False)}")

            # 执行工具
            if func_name in TOOL_MAP:
                result = TOOL_MAP[func_name](**func_args)
                print(f"   结果: {json.dumps(result, ensure_ascii=False)}")

                # 将 assistant 消息和工具结果追加到对话历史
                messages.append(response.message)
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_name": func_name
                })
            else:
                print(f"   错误：未知的工具 {func_name}")
                return f"未知的工具: {func_name}"

        # 第二次调用：根据工具结果生成最终回答
        final_response = ollama.chat(
            model=model,
            messages=messages,
            tools=tools
        )
        return final_response.message.content
    else:
        # 模型认为不需要调用工具，直接返回文本回答
        return response.message.content

if __name__ == "__main__":
    test_queries = [
        #"帮我扫描一下 localhost 的 80 端口是否开放",
        #"检查 example.com 是否存在 SQL 注入漏洞",
        "帮我扫描一下我192.168.101.0 24有哪些主机"
        #"分析一下常见的 Web 安全漏洞"  # 不需要工具的问题
    ]
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"问题: {query}")
        print("="*60)
        result = chat_with_tools(query)
        print(f"\n💬 回答: {result}")
        
        

