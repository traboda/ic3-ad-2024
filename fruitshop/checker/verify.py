from ctypes import c_ulonglong, cdll
import json

# This requires the auth.so and the function_order.json
# file created by src/generate.py file

# Load the auth.so library and set the return value
# of functions
auth = cdll.LoadLibrary("./auth.so")
auth.func1.restype = c_ulonglong
auth.func2.restype = c_ulonglong
auth.func3.restype = c_ulonglong
auth.func4.restype = c_ulonglong
auth.func5.restype = c_ulonglong
auth.func6.restype = c_ulonglong
auth.func7.restype = c_ulonglong
auth.func8.restype = c_ulonglong


def f1(x):
    return auth.func1(c_ulonglong(x))


def f2(x):
    return auth.func2(c_ulonglong(x))


def f3(x):
    return auth.func3(c_ulonglong(x))


def f4(x):
    return auth.func4(c_ulonglong(x))


def f5(x):
    return auth.func5(c_ulonglong(x))


def f6(x):
    return auth.func6(c_ulonglong(x))


def f7(x):
    return auth.func7(c_ulonglong(x))


def f8(x):
    return auth.func8(c_ulonglong(x))


# function_order.json contains mapping between
# binary -> order of signature function
# {"0": [true, false, true, false, false, true, false, false],
#  "1": [true, true, true, false, false, false, false, false]}
with open("functions_order.json", "r") as f:
    func_order = json.load(f)


def get_func_order(no):
    return func_order[str(no)]


# order = array contining true/false if the
# function is embedded in the binary
# [True, False, True, False, False, True, False, False]
def sign(binary_no, x):
    order = get_func_order(binary_no)
    # we are using 8 functions
    assert len(order) == 8
    for i in range(4):
        if order[0]:
            x = f1(x)
        if order[1]:
            x = f2(x)
        if order[2]:
            x = f3(x)
        if order[3]:
            x = f4(x)
        if order[4]:
            x = f5(x)
        if order[5]:
            x = f6(x)
        if order[6]:
            x = f7(x)
        if order[7]:
            x = f8(x)
    return x
