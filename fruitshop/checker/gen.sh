#!/bin/sh
set -x
# pip install grpcio grpcio-tools
python3 -m grpc_tools.protoc -I proto/ --python_out=. --grpc_python_out=. checker.proto

