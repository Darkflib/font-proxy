#!/bin/bash

# This script is used to run the Python script with the specified arguments.

# source ./venv/bin/activate # Activate the virtual environment on Linux and MacOS
source .venv/Scripts/activate # Uncomment this line for Windows
source .env # Load environment variables from .env file

# Check if the cert and key files exist
if [ ! -f "cert.pem" ]; then
    echo "Certificate file not found: cert.pem"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout "key.pem" -out "cert.pem" -subj "/CN=localhost"
    echo "Certificate file created"
fi

flask run --host=0.0.0.0 --port=5000 --cert=cert.pem --key=key.pem --debug

deactivate # Deactivate the virtual environment

# Note: The script assumes that the virtual environment is located in the same directory as the script.