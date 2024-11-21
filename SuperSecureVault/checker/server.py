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

import checker_pb2 as checker
import checker_pb2_grpc as checker_grpc


def gen_rand_str(length):
    return "".join(
        random.SystemRandom().choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )


creds = {
    "10.42.1.2": "55lpeWRNEWpx",
    "10.42.1.3": "mEyP4BDV1tJH",
    "10.42.1.4": "h8XzbBIiIvSh",
    "10.42.1.5": "43naBQlhnkjI",
    "10.42.1.6": "uH8W75Hu5uGp",
    "10.42.1.7": "WBh3HhdqyzBY",
    "10.42.1.8": "gNgJAmCQV7lu",
    "10.42.1.9": "bJlGXSD7oPGv",
    "10.42.1.10": "TJQYg4Eq6iGB",
    "10.42.1.11": "feFEreu8nPH3",
}


def register(r, ip, port, username, email, password):
    url = f"http://{ip}:{port}/register"

    try:
        payload = {"name": username, "password": password, "email": email}

        response = r.post(url, data=payload, timeout=5, allow_redirects=False)

        if response.status_code == 302:
            if response.headers["Location"] == "/login":
                status = checker.ServiceState.UP
                service_status = checker.ServiceStatus(state=status, reason="")
                return (True, service_status)
            elif response.headers["Location"] == "/error":
                status = checker.ServiceState.MUMBLE
                reason = response.json()["message"]
                service_status = checker.ServiceStatus(state=status, reason=reason)
                return (False, service_status)
            status = checker.ServiceState.DOWN
            reason = "Registration Failed"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return (False, service_status)
        else:
            status = checker.ServiceState.DOWN
            reason = "Registration Failed"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return (False, service_status)

    except requests.ConnectionError:
        status = checker.ServiceState.DOWN
        reason = "Unable to connect to the server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)
    except requests.Timeout:
        status = checker.ServiceState.DOWN
        reason = "Request timed out"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)
    except KeyError:
        status = checker.ServiceState.MUMBLE
        reason = "Invalid JSON response from server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)
    except Exception as e:
        print(e)
        status = checker.ServiceState.DOWN
        reason = "Unexpected error during registration"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)


def login(r, ip, port, email, password):
    url = f"http://{ip}:{port}/login"

    try:
        payload = {"password": password, "email": email}

        response = r.post(url, data=payload, timeout=5, allow_redirects=False)

        if response.status_code == 302:
            if response.headers["Location"] == "/home":
                status = checker.ServiceState.UP
                service_status = checker.ServiceStatus(state=status, reason="")
                return (True, service_status)
            elif response.headers["Location"] == "/error":
                status = checker.ServiceState.MUMBLE
                reason = response.json()["message"]
                service_status = checker.ServiceStatus(state=status, reason=reason)
                return (False, service_status)
            status = checker.ServiceState.DOWN
            reason = "Login Failed"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return (False, service_status)
        else:
            status = checker.ServiceState.DOWN
            reason = "Login Failed"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return (False, service_status)

    except requests.ConnectionError:
        status = checker.ServiceState.DOWN
        reason = "Unable to connect to the server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)
    except requests.Timeout:
        status = checker.ServiceState.DOWN
        reason = "Request timed out"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)
    except KeyError:
        status = checker.ServiceState.MUMBLE
        reason = "Invalid JSON response from server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)
    except Exception as e:
        print(e)
        status = checker.ServiceState.DOWN
        reason = "Unexpected error during login"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)


def view_item(r, ip, port, flag):
    url = f"http://{ip}:{port}/inventory/view"

    try:
        response = r.get(url, timeout=5)

        if response.status_code == 200:
            if response.json()["status"] == True:
                if flag in response.content.decode():
                    status = checker.ServiceState.UP
                    service_status = checker.ServiceStatus(state=status, reason="")
                    return service_status
                else:
                    status = checker.ServiceState.CORRUPT
                    reason = "Flag not found"
                    service_status = checker.ServiceStatus(state=status, reason=reason)
                    return service_status
            status = checker.ServiceState.MUMBLE
            reason = "Unable to retrieve flag"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return service_status
        else:
            status = checker.ServiceState.MUMBLE
            reason = "Unable to retrieve flag"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return service_status

    except requests.ConnectionError:
        status = checker.ServiceState.DOWN
        reason = "Unable to connect to the server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except requests.Timeout:
        status = checker.ServiceState.DOWN
        reason = "Request timed out"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except KeyError:
        status = checker.ServiceState.MUMBLE
        reason = "Invalid JSON response from server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except Exception as e:
        print(e)
        status = checker.ServiceState.DOWN
        reason = f"Error while retrieving flag"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status


def add_item(r, ip, port, name, code, description):
    url = f"http://{ip}:{port}/inventory/addItem"

    try:
        payload = {
            "name": name,
            "code": code,
            "description": description,
        }

        response = r.post(url, data=payload, timeout=5, allow_redirects=False)

        if response.status_code == 302:
            if (
                response.headers["Location"] == "/add"
                and response.json()["status"] == True
            ):
                status = checker.ServiceState.UP
                service_status = checker.ServiceStatus(state=status, reason="")
                return (True, service_status)
            elif response.headers["Location"] == "/error":
                status = checker.ServiceState.MUMBLE
                reason = response.json()["message"]
                service_status = checker.ServiceStatus(state=status, reason=reason)
                return (False, service_status)
            status = checker.ServiceState.DOWN
            reason = "Not able to add Item to Inventory"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return (False, service_status)
        else:
            status = checker.ServiceState.DOWN
            reason = "Not able to add Item to Inventory"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return (False, service_status)

    except requests.ConnectionError:
        status = checker.ServiceState.DOWN
        reason = "Unable to connect to the server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)
    except requests.Timeout:
        status = checker.ServiceState.DOWN
        reason = "Request timed out"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)
    except KeyError:
        status = checker.ServiceState.MUMBLE
        reason = "Invalid JSON response from server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)
    except Exception as e:
        print(e)
        status = checker.ServiceState.DOWN
        reason = "Unexpected error during adding Item to Inventory"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status)


def add_secure_item(r, ip, port, sid, message, name, code, description):
    url = f"http://{ip}:{port}/secureinventory/addItem"

    try:
        payload = {
            "sid": sid,
            "message": message,
            "name": name,
            "code": code,
            "description": description,
        }

        response = r.post(url, data=payload, timeout=5, allow_redirects=False)

        if response.status_code == 303:
            if (
                "/token" in response.headers["Location"]
                and response.json()["status"] == True
            ):
                token = response.json()["securestorage"]["token"]
                status = checker.ServiceState.UP
                service_status = checker.ServiceStatus(state=status, reason="")
                return (True, service_status, token)
            elif response.headers["Location"] == "/error":
                status = checker.ServiceState.MUMBLE
                reason = response.json()["message"]
                service_status = checker.ServiceStatus(state=status, reason=reason)
                return (False, service_status, "")
            status = checker.ServiceState.DOWN
            reason = "Not able to add Item to Secure Inventory"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return (False, service_status, "")
        else:
            status = checker.ServiceState.DOWN
            reason = "Not able to add Item to Secure Inventory"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return (False, service_status, "")

    except requests.ConnectionError:
        status = checker.ServiceState.DOWN
        reason = "Unable to connect to the server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status, "")
    except requests.Timeout:
        status = checker.ServiceState.DOWN
        reason = "Request timed out"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status, "")
    except KeyError:
        status = checker.ServiceState.MUMBLE
        reason = "Invalid JSON response from server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status, "")
    except Exception as e:
        print(e)
        status = checker.ServiceState.DOWN
        reason = "Unexpected error during adding Item to Secure Inventory"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (False, service_status, "")


def view_secure_item(r, ip, port, sid, message, token, flag):
    url = f"http://{ip}:{port}/secureinventory/viewItem"

    try:

        payload = {"sid": sid, "message": message, "token": token}
        print(payload)
        response = r.post(url, data=payload, timeout=5, allow_redirects=False)
        if response.status_code == 200:
            if response.json()["status"] == True:
                if flag in response.content.decode():
                    status = checker.ServiceState.UP
                    service_status = checker.ServiceStatus(state=status, reason="")
                    return service_status
                else:
                    print(response.content.decode())
                    status = checker.ServiceState.CORRUPT
                    reason = "Flag not found"
                    service_status = checker.ServiceStatus(state=status, reason=reason)
                    return service_status

            status = checker.ServiceState.MUMBLE
            reason = response.json()["message"]
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return service_status
        elif response.status_code == 302 and response.headers["Location"] == "/error":
            status = checker.ServiceState.MUMBLE
            reason = response.json()["message"]
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return service_status
        else:
            status = checker.ServiceState.MUMBLE
            reason = "Unable to retrieve flag"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return service_status

    except requests.ConnectionError:
        status = checker.ServiceState.DOWN
        reason = "Unable to connect to the server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except requests.Timeout:
        status = checker.ServiceState.DOWN
        reason = "Request timed out"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except KeyError:
        status = checker.ServiceState.MUMBLE
        reason = "Invalid JSON response from server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except Exception as e:
        print(e)
        status = checker.ServiceState.DOWN
        reason = f"Error while retrieving flag"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status


def plant_flag(ip, port, flag, slot):
    try:
        r = requests.Session()

        username = gen_rand_str(10)
        password = gen_rand_str(10)
        email = f"{gen_rand_str(6)}@gmail.com"
        status, service_status = register(
            r=r, ip=ip, port=port, username=username, email=email, password=password
        )
        if status == False:
            return (service_status, "", "")

        status, service_status = login(
            r=r, ip=ip, port=port, email=email, password=password
        )
        if status == False:
            return (service_status, "", "")
        if slot == 1:
            name = gen_rand_str(10)
            description = gen_rand_str(10)
            status, service_status = add_item(
                r=r, ip=ip, port=port, name=name, code=flag, description=description
            )

            if status == False:
                return (service_status, "", "")

            token = f"{email}:{password}:{name}"
            identifier = f"{name}"
            print("identifier", identifier)
            status = checker.ServiceState.UP
            service_status = checker.ServiceStatus(state=status, reason="")
            return (service_status, token, identifier)
        if slot == 2:
            sid = gen_rand_str(10)
            message = gen_rand_str(12)
            message = message.encode("utf-8").hex()
            name = gen_rand_str(9)
            description = gen_rand_str(12)
            status, service_status, tok = add_secure_item(
                r=r,
                ip=ip,
                port=port,
                sid=sid,
                message=message,
                name=name,
                code=flag,
                description=description,
            )

            if status == False:
                return (service_status, "", "")

            token = f"{email}:{password}:{tok}"
            identifier = f"{sid}:{message}"
            print("identifier2: ", identifier)
            status = checker.ServiceState.UP
            service_status = checker.ServiceStatus(state=status, reason="")
            return (service_status, token, identifier)
    except requests.Timeout:
        reason = f"Unable to plant flag: Socket timeout"
        status = checker.ServiceState.DOWN
        token = ""
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (service_status, token, "")
    except requests.ConnectionError:
        reason = f"Unable to plant flag: Unable to Connect"
        status = checker.ServiceState.DOWN
        token = ""
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return (service_status, token, "")
    except Exception as e:
        print(e)
        reason = f"Unable to plant flag"
        status = checker.ServiceState.CORRUPT
        token = ""
        service_status = checker.ServiceStatus(state=status, reason=reason)

    return (service_status, token, "")


def check_flag(ip, port, flag, token, identifier, slot):
    try:
        r = requests.Session()
        if slot == 1:
            email, password, name = token.split(":")
            status, service_status = login(
                r=r, ip=ip, port=port, email=email, password=password
            )
            if status == False:
                return service_status

            service_status = view_item(r=r, ip=ip, port=port, flag=flag)
            return service_status
        if slot == 2:
            print(token)
            email, password, tok = token.split(":")
            print(identifier)
            sid, message = identifier.split(":")
            status, service_status = login(
                r=r, ip=ip, port=port, email=email, password=password
            )
            if status == False:
                return service_status
            service_status = view_secure_item(
                r=r, ip=ip, port=port, sid=sid, message=message, token=tok, flag=flag
            )
            return service_status
    except requests.Timeout:
        reason = f"Unable to retrieve flag: Socket timeout"
        status = checker.ServiceState.DOWN
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except requests.ConnectionError:
        reason = f"Unable to retrieve flag: Unable to Connect"
        status = checker.ServiceState.DOWN
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except Exception as e:
        print(e)
        reason = f"Not able to retrieve flag!"
        status = checker.ServiceState.CORRUPT
        service_status = checker.ServiceStatus(state=status, reason=reason)

    return service_status


def view_fullinventory(r, ip, port):
    url = f"http://{ip}:{port}/inventory/fullinventory"

    try:
        response = r.get(url, timeout=5)

        if response.status_code == 200:
            if response.json()["status"] == True:
                status = checker.ServiceState.UP
                service_status = checker.ServiceStatus(state=status, reason="")
                return service_status
            status = checker.ServiceState.MUMBLE
            reason = "view fullinventory page not working"
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return service_status
        else:
            status = checker.ServiceState.MUMBLE
            reason = response.json()["message"]
            service_status = checker.ServiceStatus(state=status, reason=reason)
            return service_status

    except requests.ConnectionError:
        status = checker.ServiceState.DOWN
        reason = "Unable to connect to the server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except requests.Timeout:
        status = checker.ServiceState.DOWN
        reason = "Request timed out"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except KeyError:
        status = checker.ServiceState.MUMBLE
        reason = "Invalid JSON response from server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except Exception as e:
        print(e)
        status = checker.ServiceState.DOWN
        reason = f"Error while viewing full inventory"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status


def check_service(ip, port):
    try:
        r = requests.Session()
        email = "admin@inventory.secure"
        password = creds[ip]
        status, service_status = login(
            r=r, ip=ip, port=port, email=email, password=password
        )

        if status == False:
            if service_status.state == 2:
                return service_status
            else:
                reason = "Unable to login using admin creds"
                status = checker.ServiceState.CORRUPT
                service_status = checker.ServiceStatus(state=status, reason=reason)
                return service_status
        service_status = view_fullinventory(r=r, ip=ip, port=port)
        return service_status
    except requests.ConnectionError:
        status = checker.ServiceState.DOWN
        reason = "Unable to connect to the server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except requests.Timeout:
        status = checker.ServiceState.DOWN
        reason = "Request timed out"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except KeyError:
        status = checker.ServiceState.MUMBLE
        reason = "Invalid JSON response from server"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status
    except Exception as e:
        print(e)
        status = checker.ServiceState.DOWN
        reason = f"Error while checking service"
        service_status = checker.ServiceStatus(state=status, reason=reason)
        return service_status


class Checker(checker_grpc.CheckerServicer):
    def PlantFlag(self, request, context):
        try:

            service_status, token, identifier = plant_flag(
                request.ip, request.port, request.flag, request.slot
            )
            print(
                f"Plant Flag {request.ip} -> {request.port} : {service_status.state} : {service_status.reason}"
            )
            return checker.PlantFlagResponse(
                status=service_status, token=token, identifier=identifier
            )
        except Exception as e:
            print(e)
            reason = f"Unable to Plant Flag"
            service_status = checker.ServiceStatus(
                state=checker.ServiceState.CORRUPT, reason=reason
            )
            return checker.PlantFlagResponse(
                status=service_status, token="", identifier=""
            )

    def CheckFlag(self, request, context):
        try:
            service_status = check_flag(
                ip=request.ip,
                port=request.port,
                flag=request.flag,
                token=request.token,
                identifier=request.identifier,
                slot=request.slot,
            )

            print(
                f"Checked Flag {request.ip} -> {request.port} : {service_status.state} : {service_status.reason}"
            )
        except Exception as e:
            print(e)
            state = checker.ServiceStatus.CORRUPT
            reason = f"Unable to Retrive Flag"
            service_status = checker.ServiceStatus(state=state, reason=reason)
        return service_status

    def CheckService(self, request, context):
        try:
            service_status = check_service(request.ip, request.port)
            return service_status
        except Exception as e:
            print(e)
            state = checker.ServiceState.DOWN
            reason = f"Service is down: Unable to Connect"
            service_status = checker.ServiceStatus(state=state, reason=reason)
        print(
            f"Checked Service {request.ip} -> {request.port} : {service_status.state} : {service_status.reason}"
        )
        return service_status


def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10), options=(("grpc.so_reuseport", 1),)
    )
    checker_grpc.add_CheckerServicer_to_server(Checker(), server)
    port = 50051
    print(f"Launching Server on port :: {port}")
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
