import asyncio
import json
from aiohttp import web, WSMsgType


class WSCallsManager:
    ws = None
    def __init__(self, message_handler=None):
        self.calls = dict()
        self.call_id = 0
        self.message_handler = message_handler
        self.destroyed = False
    
    async def prepare_request(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.ws = ws

    async def call(self, action, params, timeout=30):
        self.call_id += 1
        payload = {
            'call_id': self.call_id,
            'action': action,
            'params': params
        }
        loop = asyncio.get_event_loop()
        call = loop.create_future()
        self.calls[self.call_id] = (loop, call)
        
        await self.ws.send_str(json.dumps(payload))
        await asyncio.wait_for(call, timeout)
        return call.result()
    
    def handle_call(self, call_id, result=None, error=None):
        loop, call = self._get_call_and_remove(call_id)
        if (call.cancelled()):
            return
        if (error is not None):
            loop.call_soon_threadsafe(call.set_exception, ValueError(error))
        else:
            loop.call_soon_threadsafe(call.set_result, result)
    
    def _get_call_and_remove(self, call_id):
        (loop, call) = self.calls.get(call_id, None)
        if call is not None:
            self.calls.pop(call_id)
        else:
            raise ValueError(f'call {call_id} not found')
        return loop, call
    
    async def message_loop(self):
        async for msg in self.ws:
            if self.destroyed: break
            if self.message_handler is not None and await self.message_handler(msg):
                continue
            if msg.type == WSMsgType.TEXT:
                payload = json.loads(msg.data)
                if 'call_id' in payload:
                    call_id = payload['call_id']
                    if 'error' not in payload and 'result' not in payload:
                        await self.ws.send_str(json.dumps({ call_id: call_id, 'error': 'result not found in payload'}))
                    else:
                        self.handle_call(call_id, result=payload.get("result", None), error=payload.get("error", None))
                else:
                    if 'error' in payload:
                        print('Remote error', payload['error'])
                    await self.ws.send_str(json.dumps({ 'error': 'call_id not found in payload'}))
            elif msg.type == WSMsgType.ERROR:
                print('ws connection closed with exception %s' % self.ws.exception())
            else:
                await self.ws.send_str('invalid msg type')
        await self.destroy()

    async def destroy(self):
        if self.destroyed: 
            return
        self.destroyed = True
        await self.ws.close()
