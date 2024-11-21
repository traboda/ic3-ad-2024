# Start from the Go 1.22.2 base image
FROM golang:1.22.2

# Set the Working Directory inside the container
WORKDIR /app

# Copy everything to the working directory
COPY . .

# Download dependencies
RUN go mod tidy

# Build the Go app
RUN go build -o main .

# Expose port 8000
EXPOSE 8000

# Command to run the executable
CMD ["./main"]