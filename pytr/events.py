import asyncio
import json


class Events:
    def __init__(self, tr, instrument_id, exchange="LSX"):
        self.tr = tr
        self.instrument_id = instrument_id
        self.exchange = exchange

    async def events_loop(self):
        asyncio.create_task(self.tr.recv2())
        fut_queue = await self.tr.subscribe2("ticker", id=f"{self.instrument_id}.{self.exchange}")
        print(await fut_queue.get())

    def get(self):
        asyncio.get_event_loop().run_until_complete(self.events_loop())
