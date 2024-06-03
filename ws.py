import asyncio
import json
from server import PromptServer
from aiohttp import WSMsgType, web
from .ws_manager import WSCallsManager

ws_list = []

@PromptServer.instance.routes.get('/A1111/v1/init_client')
async def init_client_handler(request):
    ws = WSCallsManager()
    await ws.prepare_request(request)
    ws_list.append(ws)
    await ws.message_loop()
    ws_list.remove(ws)
    return web.Response()

async def run_prompt(random_id):
    if len(ws_list) <= 0:
        return
    for ws in ws_list:
        await ws.call("run_prompt", {'random_id': random_id}, timeout = 600)
    queue = PromptServer.instance.prompt_queue
    if not queue:
        return
    count = queue.get_tasks_remaining()
    while count > 0:
        await asyncio.sleep(1)
        count = queue.get_tasks_remaining()
    

    
