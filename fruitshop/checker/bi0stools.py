import asyncio
from hexdump import hexdump

# pyright: reportAttributeAccessIssue=false


class Context:
    def __init__(self):
        self.timeout = 10
        self.debug = True


context = Context()


class Connection:
    @classmethod
    async def remote(cls, ip, port):
        self = cls()
        self.ip = ip
        self.port = port
        self.reader, self.writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=context.timeout
        )
        return self

    async def recv(self, n):
        if context.debug:
            print('read("{}")'.format(n))
        res = await asyncio.wait_for(
            self.reader.readexactly(n), timeout=context.timeout
        )
        if context.debug:
            hexdump(res)
        return res

    async def recvuntil(self, string):
        if context.debug:
            print('readuntil("{}")'.format(string))
        res = await asyncio.wait_for(
            self.reader.readuntil(string.encode()), timeout=context.timeout
        )
        if context.debug:
            hexdump(res)

        return res

    async def recvline(self):
        if context.debug:
            print("recvline()")
        res = await asyncio.wait_for(self.reader.readline(), timeout=context.timeout)
        if context.debug:
            hexdump(res)
        return res

    async def send(self, string):
        if context.debug:
            print('send("{}")'.format(string))
            hexdump(string)

        self.writer.write(string)
        await self.writer.drain()

    async def sendline(self, string):
        if context.debug:
            print('sendline("{}")'.format(string))
            hexdump(string)

        self.writer.write(string + b"\n")
        await self.writer.drain()

    async def close(self):
        await self.writer.drain()
        self.writer.close()
        await self.writer.wait_closed()
