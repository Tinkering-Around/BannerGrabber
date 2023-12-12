# Author: Tinkering-Around

import socket
import os
import datetime
import subprocess
import re

# Prompt user for IP address
ip = input("Enter IP address to scan: ")

# Prompt user for ports to scan
ports_input = input("Enter ports to scan (comma-separated) or 'A' for all ports: ").strip().lower()

# Parse user input for ports
if ports_input == 'a':
    ports_to_scan = range(1, 65536)  # Scan all ports
else:
    try:
        ports_to_scan = [int(port.strip()) for port in ports_input.split(',')]
    except ValueError:
        print("Invalid input. Please enter a valid port number or 'A' for all ports.")
        exit()

# Generate filename based on IP and timestamp
filename = f"bannergrab_{ip}_{datetime.datetime.now().strftime('%d%m%Y_%H%M')}"

# Open file for writing results
with open(filename, "w") as file:
    # Iterate over specified ports
    for port in ports_to_scan:
        # Create a socket with a timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        try:
            # Attempt to connect to the specified IP and port
            sock.connect((ip, port))

            # If the port is 80 (HTTP), send a simple HTTP request
            if port == 80:
                sock.send(b"HEAD / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")

            # Receive banner from the service running on the port
            banner = sock.recv(1024).decode().strip()
            output = f"{ip} - {port} - {banner}"

            # Print and write the output to the file
            print(output)
            file.write(output + "\n")

            # Check for exploitability using subprocess and searchsploit
            command = f"searchsploit {banner}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            # Capture and print exploitability results
            exploit_results = result.stdout
            if "No results found" not in exploit_results:
                print(f"Potential exploits found for {banner}!")
            else:
                print(f"No exploits found for {banner}.")

        except Exception as e:
            print(f"Could not connect to {ip}:{port}")

        finally:
            sock.close()