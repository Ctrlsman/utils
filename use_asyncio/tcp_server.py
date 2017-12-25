import sys
import asyncio
import asyncio.streams


class MyServer:
    def __init__(self):
        self.server = None
        self.clients = {}

    def _accept_client(self, client_reader, client_writer):
        task = asyncio.Task(self._handle_client(client_reader, client_writer))
        self.clients[task] = (client_reader, client_writer)

        def client_done(task):
            print("client task done:", task, file=sys.stderr)
            del self.clients[task]

        task.add_done_callback(client_done)

    @asyncio.coroutine
    def _handle_client(self, client_reader, client_writer):
        while True:
            data = (yield from client_reader.readline()).decode("utf-8")
            if not data:  # an empty string means the client disconnected
                break
            cmd, *args = data.rstrip().split(' ')
            if cmd == 'add':
                arg1 = float(args[0])
                arg2 = float(args[1])
                retval = arg1 + arg2
                client_writer.write("{!r}\n".format(retval).encode("utf-8"))
            elif cmd == 'repeat':
                times = int(args[0])
                msg = args[1]
                client_writer.write("begin\n".encode("utf-8"))
                for idx in range(times):
                    client_writer.write("{}. {}\n".format(idx + 1, msg)
                                        .encode("utf-8"))
                client_writer.write("end\n".encode("utf-8"))
            else:
                print("Bad command {!r}".format(data), file=sys.stderr)

            # This enables us to have flow control in our connection.
            yield from client_writer.drain()

    def start(self, loop):
        self.server = loop.run_until_complete(
            asyncio.streams.start_server(self._accept_client,
                                         '127.0.0.1', 12345,
                                         loop=loop))

    def stop(self, loop):
        if self.server is not None:
            self.server.close()
            loop.run_until_complete(self.server.wait_closed())


def main():
    loop = asyncio.get_event_loop()

    server = MyServer()
    server.start(loop)

    @asyncio.coroutine
    def client():
        reader, writer = yield from asyncio.streams.open_connection('127.0.0.1', 12345, loop=loop)

        def send(msg):
            print('>>>:', msg)
            writer.write((msg + '\n').encode('utf-8'))

        def recv():
            msgback = (yield from reader.readline()).decode("utf-8").rstrip()
            print('<<<:', msgback)
            return msgback

        send("add 1 2")
        msg = yield from recv()

        send("repeat 5 hello")
        msg = yield from recv()
        assert msg == 'begin'
        while True:
            msg = yield from recv()
            if msg == 'end':
                break

        writer.close()
        yield from asyncio.sleep(0.5)

        # creates a client and connects to our server

    try:
        loop.run_until_complete(client())
        server.stop(loop)
    finally:
        loop.close()


if __name__ == '__main__':
    main()
