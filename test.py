import asyncio


lock = asyncio.Lock()


async def coro_one() -> None:
    while True:
        async with lock:
            print("coro_one_start")
            await asyncio.sleep(delay=3)
            print("coro_one_finish\n")

        await asyncio.sleep(delay=5)


async def coro_two() -> None:
    while True:
        async with lock:
            print("coro_two_start")
            await asyncio.sleep(delay=1)
            print("coro_two_finish\n")

        await asyncio.sleep(delay=3)


async def main() -> None:
    aio_loop = asyncio.get_event_loop()
    task_one = aio_loop.create_task(coro_one())
    task_two = aio_loop.create_task(coro_two())

    await task_one
    await task_two



if __name__ == "__main__":
    asyncio.run(main=main())