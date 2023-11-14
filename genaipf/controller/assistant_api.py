from sanic.request import Request
from concurrent.futures import ThreadPoolExecutor
from sanic.response import json
from genaipf.interfaces.common_response import success,fail
from genaipf.services import assistant_service
import os
import openai
from dotenv import load_dotenv
from genaipf.conf.assistant_conf import ASSISTANT_ID_MAPPING

load_dotenv(override=True)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

async def submit_message(assistant_id, thread, user_message):
    await client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

async def get_response(thread):
    return await client.beta.threads.messages.list(thread_id=thread.id)

async def retrieve_thread_and_run(assistant_id, thread_id, user_input):
    # thread = client.beta.threads.create()
    thread = await client.beta.threads.retrieve(thread_id)
    run = await submit_message(assistant_id, thread, user_input)
    return thread, run

async def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = await client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
        print(run.status)
    return run

async def get_assistant_response(assistant_id, thread_id, content_l):
    content = content_l[0]
    user_input = content["content"]
    thread1, run1 = await retrieve_thread_and_run(
        assistant_id, thread_id, user_input
    )
    run1 = await wait_on_run(run1, thread1)
    msgs = await get_response(thread1)
    res = "nothing"
    for m in msgs.data:
        if m.role == "assistant":
            res = m.content[0].text.value
            break
    return res
            

async def assistant_chat(request: Request):
    '''
    INPUT:
    outer_user_id, biz_id, source
    content: [
        {"type": "", "format": "", "version": "", "content": ""},
        {"type": "", "format": "", "version": "", "content": ""}
    ]
    # 参考格式 https://platform.openai.com/docs/guides/vision/quick-start
    
    MID:
    thread_id
    
    OUTPUT:
    {"type": "", "format": "", "version": "", "content": ""}
    '''
    # 解析请求体中的JSON数据
    request_params = request.json
    outer_user_id = request_params.get("outer_user_id", "")
    biz_id = request_params.get("biz_id", "")
    source = request_params.get("source", "")
    content_l = request_params.get("content", [])

    assistant_name = f'{biz_id}_____{source}'
    if assistant_name in ASSISTANT_ID_MAPPING:
        assistant_id = ASSISTANT_ID_MAPPING[assistant_name]
    else:
        assistant_id = ASSISTANT_ID_MAPPING["default"]

    # 业务逻辑code
    user_l = assistant_service.get_assistant_user_info_from_db(outer_user_id, biz_id, source)
    if len(user_l) == 0:
        thread = await client.beta.threads.create()
        thread_id = thread.id
        user_info = (
            outer_user_id,
            biz_id,
            source,
            thread_id,
            get_format_time()
        )
        await assistant_service.add_assistant_user(user_info)
        res = await get_assistant_response(assistant_id, thread_id, content_l)
    else:
        user = user_l[0]
        thread_id = user["thread_id"]
        res = await get_assistant_response(assistant_id, thread_id, content_l)

    # 构造输出JSON响应
    response_data = {
        "type": "text",
        "format": "text",
        "version": "v001",
        "content": res
    }

    return success(response_data)