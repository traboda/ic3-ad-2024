#!/usr/bin/python3
from concurrent import futures
import random
import string
from typing import Tuple
import grpc
import asyncio
import verify as ver

import checker_pb2 as checker
import checker_pb2_grpc as checker_grpc

from bi0stools import Connection, context

TOTAL_BIN = 100

TIMEOUT = 10


def gen_rand_port():
    return random.randint(0, TOTAL_BIN - 1)


def gen_rand_shop_number():
    return random.randint(0, TOTAL_BIN - 1)


def gen_rand_str(length):
    return "".join(
        random.SystemRandom().choice(string.hexdigits.lower()) for _ in range(length)
    )


async def createBasket(io, name):
    try:
        await io.recvuntil("Your Choice >> ")
        await io.send(b"1\n")
        await io.recvuntil("Enter the name of basket : ")
        await io.send((name + "\n").encode())
    except Exception:
        raise Exception("Unable to createBasket")


async def viewBasket(io):
    try:
        await io.recvuntil("Your Choice >> ")
        await io.send(b"2\n")
        await io.recvuntil("The name of Fruit is : ")
    except Exception:
        raise Exception("Unable to viewBasket")


async def addFruit(io, fruit_no, tag):
    try:
        await io.recvuntil("Your Choice >> ")
        await io.send(b"3\n")
        await io.recvuntil(">> ")
        await io.send((str(fruit_no) + "\n").encode("ascii"))
        await io.recvuntil("Enter size of tag : ")
        await io.send((str(len(tag)) + "\n").encode())
        await io.recvuntil("Enter tag of Fruit : ")
        await io.send((tag + "\n").encode())

    except Exception:
        raise Exception("Unable to addFruit")


async def removeFruit(io, idx):
    try:
        await io.recvuntil("Your Choice >> ")
        await io.send(b"4\n")
        await io.recvuntil("Enter the fruit id : ")
        await io.send(idx)

    except Exception:
        raise Exception("Unable to removeFruit")


async def storeBasket(io):
    try:
        await io.recvuntil("Your Choice >> ")
        await io.send(b"5\n")
        await io.recvuntil("Basket tag : ")
        return await io.recvline()

    except Exception:
        raise Exception("Unable to storeBasket")


async def restoreBasket(io, tag):
    try:
        await io.recvuntil("Your Choice >> ")
        await io.send(b"6\n")
        await io.recvuntil("Basket tag : ")
        await io.send((tag + "\n").encode())
    except Exception:
        raise Exception("Unable to restoreBasket")


async def checkSignature(io, val):
    try:
        await io.recvuntil("Your Choice >> ")
        await io.send(b"4919\n")
        await io.recvuntil("Enter the number : ")
        await io.send((str(val) + "\n").encode("ascii"))
        res = await io.recvline()
        res = int(res.strip(), 16)
        return res
    except Exception:
        raise Exception("Unable to checkSignature")


async def removeBasket(io, tag):
    try:
        await io.recvuntil("Your Choice >> ")
        await io.send(b"7\n")
        await io.recvuntil("Basket tag : ")
        await io.send((tag + "\n").encode())
    except Exception:
        raise Exception("Unable to removeBasket")


async def selectFruitShop(io, number):
    try:
        await io.recvuntil("Which shop do you want to enter: ")
        await io.send((str(number) + "\n").encode("ascii"))
    except Exception:
        raise Exception("Unable to select FruitShop: %s" % (str(number)))


# This function plants a flag in a random shop
# The token format is <shop_number>:<basket_hash>
async def set_flag(ip, port, flag_id, flag) -> Tuple[checker.ServiceStatus, str]:
    try:
        io = await Connection.remote(ip, port)
        shop_no = gen_rand_shop_number()
        await selectFruitShop(io, shop_no)
        basket_name = flag_id
        await createBasket(io, basket_name)
        fruit_no = random.randint(1, 5)
        await addFruit(io, fruit_no, flag)
        token = await storeBasket(io)
        token = "%s:%s" % (str(shop_no), str(token.strip().decode("utf-8")))

        await io.close()

    except Exception as e:
        reason = str(e)
        reason = "Unable to Set Flag: %s" % (reason)
        state = checker.ServiceState.DOWN
        status = checker.ServiceStatus(state=state, reason=reason)
        return (status, "")

    status = checker.ServiceStatus(state=checker.ServiceState.UP, reason="")
    return (status, token)


# This function checks if the flag exists in a shop
async def flag_binary(ip, port, flag, token):
    try:
        shop_no = int(token.split(":")[0])
        tag = token.split(":")[1]
        io = await Connection.remote(ip, port)
        await selectFruitShop(io, shop_no)
        await restoreBasket(io, tag)
        await viewBasket(io)
        cur_flag = await io.recv(len(flag))
        cur_flag = cur_flag.strip().decode("utf-8")
        await io.close()
        if flag == cur_flag:
            return
        else:
            raise Exception("Invalid flag retreived")

    except Exception as msg:
        try:
            await io.close()
        except Exception:
            pass
        raise Exception("Unable to retrive flag: %s" % msg)


# This function checks different functionality of the service, including verifying the signature of the binary
async def check_functionality(
    ip: str, port: int, shop_no: int
) -> checker.ServiceStatus:
    try:
        io = await Connection.remote(ip, port)
    except Exception:
        state = checker.ServiceState.DOWN
        reason = "Unable to connect to {}:{}".format(ip, port)
        return checker.ServiceStatus(state=state, reason=reason)

    try:
        await selectFruitShop(io, shop_no)
        # First we check whether the binary was changed or not
        check_val = random.randint(0x0EADBEEF, 0xFEADBEEF)
        res = await checkSignature(io, check_val)
        if not (res == ver.sign(shop_no, check_val)):
            state = checker.ServiceState.MUMBLE
            raise Exception("Signature is wrong".format())

        # If the binary is ok then we continue cheking other functionalities
        # First we create a basket, add a fruit and save it
        file_name = gen_rand_str(10)
        await createBasket(io, file_name)
        fruit_no = random.randint(1, 5)
        fruit_tag = gen_rand_str(10)
        await addFruit(io, fruit_no, fruit_tag)

        tag = await storeBasket(io)
        tag = tag.strip().decode("utf-8")

        # Next we try to view the basket
        await viewBasket(io)
        res = await io.recv(len(fruit_tag))
        res = res.strip().decode("utf-8")
        if not (res == fruit_tag):
            raise Exception(
                "Expected %s got %s in viewBasket of %d" % (fruit_tag, res, ip)
            )

        # Now we restore the basket and view it
        await restoreBasket(io, tag)
        await viewBasket(io)
        res = await io.recv(len(fruit_tag))
        res = res.strip().decode("utf-8")
        if not (res == fruit_tag):
            raise Exception("Expected %s got %s in viewBasket" % (string, res))

        # Deleting the created file
        await removeBasket(io, tag)

        state = checker.ServiceState.UP
        reason = ""

    except Exception as msg:
        state = checker.ServiceState.MUMBLE
        reason = "Error in binary {}:{} : {}".format(ip, port, str(msg))

    await io.close()
    return checker.ServiceStatus(state=state, reason=reason)


async def limit_connections(sem, ip, port, shop_no):
    async with sem:
        return await check_functionality(ip, port, shop_no)


async def check_service(ip, port, total_no):
    # This is to check all the binaries
    # TODO: don't check the service if it's already checked
    task = []
    sem = asyncio.Semaphore(30)
    for i in range(total_no):
        task.append(
            asyncio.create_task(
                limit_connections(sem, ip, port, gen_rand_shop_number())
            )
        )
    binary_status = await asyncio.gather(*task)
    return binary_status


async def get_flag(ip, port, flag, token) -> checker.ServiceStatus:
    try:
        # This is to check whether the flag file was removed
        await flag_binary(ip, port, flag, token)
        state = checker.ServiceState.UP
        return checker.ServiceStatus(state=state, reason="")

    except Exception as msg:
        state = checker.ServiceState.CORRUPT
        reason = "Error: %s" % str(msg)
        return checker.ServiceStatus(state=state, reason=reason)


class Checker(checker_grpc.CheckerServicer):
    def PlantFlag(self, request, context):
        flag_id = gen_rand_str(10)
        status, token = asyncio.run(
            set_flag(request.ip, request.port, flag_id, request.flag)
        )
        print("Plant Flag {} -> {} : {} ".format(request.ip, request.port, status))
        return checker.PlantFlagResponse(status=status, token=token, identifier=flag_id)

    def CheckFlag(self, request, context):
        status = asyncio.run(
            get_flag(request.ip, request.port, request.flag, request.token)
        )
        print("Check Flag {} -> {} : {}".format(request.ip, request.port, status))
        return status

    def CheckService(self, request, context):
        # TODO: Decide how many binaries to check
        no_binaries_to_check = int((TOTAL_BIN * 1))
        print("Check Service {} -> {} ".format(request.ip, request.port))
        service_states = asyncio.run(
            check_service(request.ip, request.port, no_binaries_to_check)
        )

        total = len(service_states)
        print("Checked :: %d service" % (total))
        if total == 1:
            return service_states[0]

        count_up = 0
        count_mumble = 0
        count_corrupt = 0
        count_down = 0
        reason = []
        for status in service_states:
            if status.state == checker.ServiceState.UP:
                count_up += 1
                continue
            print(status)
            if status.state == checker.ServiceState.DOWN:
                reason.append(status.reason)
                count_down += 1
            elif status.state == checker.ServiceState.MUMBLE:
                reason.append(status.reason)
                count_mumble += 1
            elif status.state == checker.ServiceState.CORRUPT:
                reason.append(status.reason)
                count_corrupt += 1

        print(count_up, count_down, count_corrupt, count_mumble)

        if len(reason) > 5:
            reason = reason[:5]
        reason = "\n\t".join(reason)

        if count_down / float(total) > 0.50:
            state = checker.ServiceState.DOWN
            reason = "{}/{} of the Service seems to be DOWN \n\t{}".format(
                count_down, total, reason
            )

        elif (count_mumble + count_down) / float(total) > 0.50:
            state = checker.ServiceState.MUMBLE
            reason = "{}/{} of the Service seems to be MUMBLE/DOWN \n\t{}".format(
                count_down + count_mumble, total, reason
            )
        else:
            state = checker.ServiceState.UP
            reason = ""

        # CheckService Does not return the error of all the services
        return checker.ServiceStatus(state=state, reason=reason)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    checker_grpc.add_CheckerServicer_to_server(Checker(), server)
    port = 50051
    print("Launching Server on port :: {}".format(port))
    server.add_insecure_port("[::]:{}".format(port))
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    context.debug = False
    serve()
