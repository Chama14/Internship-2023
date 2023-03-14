import asyncio
import nats
import time

from nats.errors import ConnectionClosedError, TimeoutError, NoServersError

async def main():
    # It is very likely that the demo server will see traffic from clients other than yours.
    # To avoid this, start your own locally and modify the example to use it.
    nc = await nats.connect()

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    async def req_callback(msg):
        print(f"Received a message on '{msg.subject} {msg.reply}': {msg.data.decode()}")
        await nc.publish(msg.reply, b'YOO')
        #await msg.respond(b'a response')

    await nc.subscribe("test_2_le_retour", cb=req_callback)

    # Simple publisher and async subscriber via coroutine.
    sub = await nc.subscribe("test", cb=message_handler)

    # Stop receiving after 3 messages.
    await sub.unsubscribe(limit=3)
    await nc.publish("test", b'Hello')
    await nc.publish("test", b'World')
    await nc.publish("test", b'!!!!!')
    await nc.publish("test", b'mmmmmh ...')


    try:
        async for msg in sub.messages:
            print(f"Received a message on '{msg.subject} {msg.reply}': {msg.data.decode()}")
            await sub.unsubscribe()
    except Exception as e:
        pass

    try:
        start_time = time.perf_counter()
        response = await nc.request("test_2_le_retour", b'hey', timeout=0.5)
        print("Received response: {message}".format(
            message=response.data.decode()))
        end_time = time.perf_counter()
        print(end_time - start_time, "seconds")

    except TimeoutError:
        print("Request timed out")

    # Remove interest in subscription.
    await sub.unsubscribe()

    # Terminate connection to NATS.
    await nc.drain()

if __name__ == '__main__':
    asyncio.run(main())