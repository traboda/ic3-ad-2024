#!/usr/bin/env bash
# https://github.com/fullstorydev/grpcurl
# set -x

# Check if IP and port for gRPC server and challenge are provided
if [ $# -ne 4 ]; then
    echo "Usage: $0 <GRPC_IP> <GRPC_PORT> <CHALLENGE_IP> <CHALLENGE_PORT>"
    exit 1
fi

# Global variables for gRPC server
GRPC_IP=$1
GRPC_PORT=$2
GRPC_ADDRESS="${GRPC_IP}:${GRPC_PORT}"

# Global variables for challenge
CHALLENGE_IP=$3
CHALLENGE_PORT=$4

PROTO_FILE="../checker/proto/checker.proto"

# Check if the proto file exists
if [ ! -f "$PROTO_FILE" ]; then
    echo "Error: Proto file not found at $PROTO_FILE"
    exit 1
fi

# Function to generate a flag in the format flag{32 hex characters}
generate_flag() {
    hex_chars=$(openssl rand -hex 16)
    echo "flag{$hex_chars}"
}

# Function to print JSON in a formatted way
print_json() {
    echo "$1" | jq '.'
    echo
}

# Function to print gRPC message
print_grpc_message() {
    echo "Sending gRPC message:"
    print_json "$1"
}

# Function to print response
print_response() {
    echo "Response:"
    print_json "$1"
}

# Function to calculate time difference in milliseconds
time_diff_ms() {
    local start=$1
    local end=$2
    echo $((end - start))
}

# Function to get current time in milliseconds
get_time_ms() {
    echo $(date +%s%3N)
}

# Function to check service
check_service() {
    echo "[*] Checking service..."
    local message='{"ip":"'"$CHALLENGE_IP"'","port":'"$CHALLENGE_PORT"'}'
    print_grpc_message "$message"
    local response=$(grpcurl -plaintext -proto "$PROTO_FILE" -d "$message" $GRPC_ADDRESS checker.Checker/CheckService)
    print_response "$response"
}

TOKEN=""
# Function to plant flag
plant_flag() {
    local flag=$1
    
    echo "[*] Planting flag..."
    local message='{"ip":"'"$CHALLENGE_IP"'","port":'"$CHALLENGE_PORT"',"flag":"'"$flag"'","slot":1}'
    print_grpc_message "$message"
    local response=$(grpcurl -plaintext -proto "$PROTO_FILE" -d "$message" $GRPC_ADDRESS checker.Checker/PlantFlag)
    print_response "$response"
    
    local token=$(echo "$response" | jq -r '.token')
    if [ -z "$token" ] || [ "$token" == "null" ]; then
        echo "Failed to extract token from PlantFlag response"
        return 1
    fi
    
    TOKEN=$token
}

# Function to check flag
check_flag() {
    local flag=$1
    local token=$2
    
    echo "[*] Checking flag..."
    local message='{"ip":"'"$CHALLENGE_IP"'","port":'"$CHALLENGE_PORT"',"flag":"'"$flag"'","token":"'"$token"'","slot":1}'
    print_grpc_message "$message"
    local response=$(grpcurl -plaintext -proto "$PROTO_FILE" -d "$message" $GRPC_ADDRESS checker.Checker/CheckFlag)
    print_response "$response"
}

# Main execution
echo "Starting gRPC service test..."

# Check service
check_service

# Generate flag and plant it
FLAG=$(generate_flag)
echo "Generated Flag: $FLAG"
plant_flag "$FLAG"

if [ $? -ne 0 ]; then
    echo "Failed to plant flag"
    exit 1
fi

# Check the planted flag
check_flag "$FLAG" "$TOKEN"

# Run check_service in parallel and measure time
PARALLEL_INSTANCES=1

echo "Running $PARALLEL_INSTANCES check_service instances in parallel..."
start_time=$(get_time_ms)

for i in $(seq 1 $PARALLEL_INSTANCES); do
    check_service $i &
done

# Wait for all background processes to finish
wait

end_time=$(get_time_ms)
execution_time=$(time_diff_ms $start_time $end_time)

echo "Parallel check_service execution completed in $execution_time milliseconds"

echo "gRPC service test completed."
