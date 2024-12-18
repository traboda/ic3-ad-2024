#!/usr/bin/env python3
import random
import json
import os
import sys


def system(command):
    print("[*] " + command)
    os.system(command)


if len(sys.argv) <= 1:
    print("{} <no of binariess to create>".format(sys.argv[0]))
    exit()

b_count = int(sys.argv[1])
fd = open("functions_order.json", "w")

if os.path.exists("market"):
    print("Error: 'market' directory already exists.")
    exit(1)

system("clang fruitshop.c -shared -DSHARED -o auth.so")
system("mkdir -p market")
system("clang market.c -o market/market -DCOUNT=%s" % (str(b_count)))
system("mkdir market/bin")

function_order = {}

for i in range(b_count):
    func = [False for _ in range(8)]
    canary = random.randint(0x0EADBEEF, 0xFEADBEEF)
    # Random size should always be greater than 10 since this is the minimum tag size in the code
    random_size = random.randint(50, 600)
    random_size = random_size - random_size % 8
    rand_func = []
    already = []
    func_times = random.randint(1, 6)
    for j in range(func_times):
        func_no = (random.randint(50, 1000) % 8) + 1
        if func_no not in already and func_no != 0:
            rand_func.append(func_no)
            already.append(func_no)

    auth_func = ""
    for k in rand_func:
        auth_func += " -DFUNC%d " % (k)
        func[k - 1] = True

    function_order[i] = func
    seed = 0x1A4 + i
    system(
        "clang -frandomize-layout-seed=%s -no-pie -Wno-format-security \
            fruitshop.c -D CANARY=%s -D  SIZE=%s %s -o bin%s -lcrypto -g"
        % (str(seed), str(canary), str(random_size), str(auth_func), str(i))
    )
    system("strip bin%s" % str(i))
    system("mv bin%s market/bin/shop-%s" % (str(i), str(i)))
    system("mkdir -p market/storeroom-%s" % (str(i)))

system("cp shop market/")
system("cp -r assets market/")
system("tar -czf market.tar.gz market")

fd.write(str(json.dumps(function_order)))
fd.close()
