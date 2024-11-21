#!/usr/bin/env python3
from concurrent import futures
import logging
import random
import string
import socket
import requests
import json
import grpc
import time

import socket
import base64
import secrets
import struct

import checker_pb2 as checker
import checker_pb2_grpc as checker_grpc


def gen_rand_str(length):
    return "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )


def recv_msg(sock):
    ln = sock.recv(4)
    ln = struct.unpack("<I",ln)[0]
    msg = sock.recv(ln)
    while (len(msg))!=ln:
        msg += sock.recv(ln-len(msg))
    return(msg)

def recv_uip(sock):
    msg = b""
    while(1):
        tmp_msg = recv_msg(sock)
        msg += tmp_msg
        if(tmp_msg==b"\n>"):
            break
    return msg

def cret_sock(ip,port):
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cs.settimeout(2)
    cs.connect((ip, port))
    return cs

def login_register(sock,uname=b"",passwd=b""):
    un = uname
    ps = passwd
    if (not un) or (not ps):
        un = gen_rand_str(10).encode()
        ps = secrets.token_bytes(8)
    rumsg = recv_msg(sock)
    print(rumsg)
    if(rumsg!=b"\nEnter Username: "):
        raise Exception("Registration failure")
    sock.send(un)
    if(recv_msg(sock)!=b"\nEnter Password: "):
        raise Exception("Registration failure")
    sock.send(ps)
    return (un,ps)


def cret_login(ip,port,uname=b"",passwd=b""):
    try:
        sock = cret_sock(ip,port)
        uname,passwd = login_register(sock,uname,passwd)
    return (sock,uname,passwd)
    

def win_game(sock):
    SOH=b'SOUTH OF HOUSE\n\nYou are facing the south side of a white house. There is a window left open here and it seems like you can just about squeeze through the opening. There is also a grave marked with a wodden cross a little farther away from the house.\n\nYou currently see the following items in the room:\n\t[*] A Wodden Cross\nYou currently see the following exits:\n\t[*] WEST OF HOUSE\n\t[*] INSIDE THE HOUSE\n\n>'

    ITH=b'INSIDE THE HOUSE\n\nYou see a large living room with a cozy fireplace. There are two boarded up doors to what you assume are kitchen and the upper floor. There is a note here and a giant sword mounted by the fireplace.\n\nYou currently see the following items in the room:\n\t[*] A Normal Sword\nYou currently see the following exits:\n\t[*] SOUTH OF HOUSE\n\n>'

    ANS=b'\nYou grab the giant sword from the matlepiece and put it away in your backpack.\nINSIDE THE HOUSE\n\nYou see a large living room with a cozy fireplace. There are two boarded up doors to what you assume are kitchen and the upper floor. There is a note here and a giant sword mounted by the fireplace.\n\nYou currently see the following items in the room:\n\t[*] A Normal Sword\nYou currently see the following exits:\n\t[*] SOUTH OF HOUSE\n\n>'

    AWC=b'\nAs you move your arm forward to touch it, it teleports you away to someplace else!\nAT CAVE ENTRANCE\n\nYou are in front of a dark looming cave. You can hear low growls of a large beast from inside. You also see the path through which you came here.\n\nThere are no items in the room.You currently see the following exits:\n\t[*] NORTH OF HOUSE\n\t[*] INSIDE THE CAVE\n\n>'

    ITC=b'INSIDE THE CAVE\n\nTotal darkness, you can see a small red glow coming from what appears to a large red blood diamond. Before you get a chance to observe it up close, you hear a monstrous roar in front of you.\n\nYou thrust your sword forward and pierce the heart of whatever monstrosity is in front of you.\n\nYou currently see the following items in the room:\n\t[*] A Red Diamond\nYou currently see the following exits:\n\t[*] AT CAVE ENTRANCE\n\n>'

    ARD=b'\nAs you move your arm forward to touch it, it teleports you away to someplace else!\nINSIDE WINNERS ROOM\n\nCongrats, you have beaten this short demo. You can record your victory message using the scribe or use the blue diamond to try the game out again.\n\nYou currently see the following items in the room:\n\t[*] A Blue Diamond\n\t[*] The Rat Scribe\nYou cannot see any exits from the room.\n>'

    steps = ["mov SOH","mov ITH","take ANS","mov SOH","take AWC","mov ITC","take ARD"]
    descs = {"mov SOH":SOH,"mov ITH":ITH,"take ANS":ANS,"take AWC":AWC,"mov ITC":ITC,"take ARD":ARD}
    recv_uip(sock)
    for i in steps:
        sock.send(i.encode())
        recved_inp = recv_uip(sock)
        if(recved_inp!=descs[i]):
            raise Exception("Garbled response from server")

def correct_ip(ip):
    ips = ip.split('.')
    cip = ""
    cip += ips[0]+"."+ips[1]+".2."+ips[3]
    return cip

def plant_flag(ip, port, flag, slot):
    TRS = b'\nThe rat squeaks in your hands and you somehow are able to make sense of it, it asks you to tell it the message so that it can be recorded.\n'

    ip = correct_ip(ip)
    cs,uname,passwd = cret_login(ip,port)
    print(uname,passwd)
    win_game(cs)
    cs.send(b"take TRS")
    if(TRS != recv_msg(cs)):
        raise Exception("Garbled response from server")
    cs.send(flag.encode())
    cs.shutdown(socket.SHUT_RDWR)
    cs.close()
    passwd = base64.b64encode(passwd)
    token = f"{uname.decode()}:{passwd.decode()}"
    identifier = uname.decode()
    return (token,identifier)

def check_flag(ip, port, flag, token, identifier, slot):
    TRS = b'\nThe rat squeaks in your hands and you somehow are able to make sense of it, it asks you to tell it the message so that it can be recorded.\n'
    TRS2 = b'\nThe rat says that you had already recorded a message.\n'

    ip = correct_ip(ip)
    uname, passwd = token.split(":")
    passwd = base64.b64decode(passwd.encode())
    uname = uname.encode()
    print(uname,passwd)
    cs,_,_ = cret_login(ip,port,uname,passwd)
    win_game(cs)
    cs.send(b"take TRS")
    if(TRS!=recv_msg(cs)):
        raise Exception("Garbled response from server")
    if(TRS2!=recv_msg(cs)):
        raise Exception("Garbled response from server")
    gflag = recv_msg(cs)
    print(gflag)
    print(gflag==flag.encode())
    if(gflag!=flag.encode()):
        raise RuntimeError("Can't Retrieve correct flag")

def check_service(ip,port):
    TRS=b'\nThe rat squeaks in your hands and you somehow are able to make sense of it, it asks you to tell it the message so that it can be recorded.\n'
    TRS2 = b'\nThe rat says that you had already recorded a message.\n'
    
    ip = correct_ip(ip)
    flag = "flag{"+gen_rand_str(32)+"}"
    token,_ = plant_flag(ip,port,flag,1)
    uname, passwd = token.split(":")
    passwd = base64.b64decode(passwd.encode())
    uname = uname.encode()
    cs,new_user,new_pass = cret_login(ip,port)
    new_pass = struct.unpack("<Q",new_pass)[0]
    print(hex(new_pass))
    print(new_user,new_pass)
    win_game(cs)
    cs.send(b"take ABD")
    if(b"\nEnter new name: "!=recv_msg(cs)):
        raise Exception("Garbled response from server")
    cs.send(uname)
    if(b"\nAs you move your arm forward to touch it, it teleports you away to someplace else!\n"!=recv_msg(cs)):
        raise Exception("Garbled response from server2")

    win_game(cs)
    cs.send(b"take TRS")
    if(TRS!=recv_msg(cs)):
        raise Exception("Garbled response from server")
    if(TRS2!=recv_msg(cs)):
        raise Exception("Garbled response from server")
    leaked_flag = recv_msg(cs)
    print(leaked_flag)
    for i in range(len(leaked_flag)):
        print(hex(leaked_flag[i]), end=",")

class Checker(checker_grpc.CheckerServicer):
    def PlantFlag(self, request, context):
        try:
            token, identifier = plant_flag(
                request.ip, request.port, request.flag, request.slot
            )
            print(token,identifier)
            print(f"Plant Flag {request.ip} -> {request.port} : UP")
            status = checker.ServiceStatus(state=checker.ServiceState.UP)
            return checker.PlantFlagResponse(
                status=status, token=token, identifier=identifier
                )
        except socket.error as e:
            reason = f"Unable to Plant Flag: Service is down"
            service_status = checker.ServiceStatus(
                state=checker.ServiceState.DOWN, reason=reason
            )
            return checker.PlantFlagResponse(
                status=service_status, token="", identifier=""
            )

        except Exception as e:
            reason = f"Unable to Plant Flag: "+str(e)
            service_status = checker.ServiceStatus(
                state=checker.ServiceState.MUMBLE, reason=reason
            )
            return checker.PlantFlagResponse(
                status=service_status, token="", identifier=""
            )

    def CheckFlag(self, request, context):
        try:
            check_flag(
                ip=request.ip,
                port=request.port,
                flag=request.flag,
                token=request.token,
                identifier=request.identifier,
                slot=request.slot,
            )

            print(
                f"Checked Flag {request.ip} -> {request.port} : UP"
            )
            status = checker.ServiceStatus(state=checker.ServiceState.UP)
            service_status = status
        except socket.error as e:
            state = checker.ServiceState.DOWN
            reason = f"Unable to Retrive Flag: Service is down"
            service_status = checker.ServiceStatus(state=state, reason=reason)
        except RuntimeError as e:
            print(str(e))
            reason = f"Unable to Retrive Flag: {str(e)}"
            service_status = checker.ServiceStatus(state=checker.ServiceState.CORRUPT, reason=reason)
        except Exception as e:
            print(str(e))
            reason = f"Unable to Retrive Flag: {str(e)}"
            service_status = checker.ServiceStatus(state=checker.ServiceState.MUMBLE, reason=reason)
        return service_status

    def CheckService(self, request, context):
        try:
            check_service(request.ip, request.port)
            status = checker.ServiceStatus(state=checker.ServiceState.UP)
            service_status = status
            return service_status
        except socket.error:
            state = checker.ServiceState.DOWN
            reason = f"Service is down: Unable to Connect"
        except Exception as e:
            state = checker.ServiceState.MUMBLE
            reason = f"Service check failed: "+str(e)
        print(f"Checked Service {request.ip} -> {request.port} : {state}")
        return checker.ServiceStatus(state=state, reason=reason)


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), options=(("grpc.so_reuseport", 1),)
    )
    checker_grpc.add_CheckerServicer_to_server(Checker(), server)
    port = 
    print(f"Launching Server on port :: {port}")
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
