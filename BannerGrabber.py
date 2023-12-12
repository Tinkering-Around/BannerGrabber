import socket
import os
import datetime
import subprocess
import re

# Get user input for IP address
ip = input("Enter IP address to scan: ")

# Get user input for ports
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

filename = f"bannergrab_{ip}_{datetime.datetime.now().strftime('%d%m%Y_%H%M')}"
with open(filename, "w") as file:
    for port in ports_to_scan:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)

        try:
            sock.connect((ip, port))

            if port == 80:  # HTTP port
                sock.send(b"HEAD / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")

            banner = sock.recv(1024).decode().strip()
            output = f"{ip} - {port} - {banner}"

            print(output)
            file.write(output + "\n")

            # Check for exploitability using subprocess
            command = f"searchsploit {banner}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)

            exploit_results = result.stdout
            if "No results found" not in exploit_results:
                print(f"Potential exploits found for {banner}!")
                # Parse the exploit results and print up to 3 examples
                exploits = re.findall(r"(\d+/\w+/[^\s]+)", exploit_results)
                for i, exploit in enumerate(exploits[:3], start=1):
                    print(f" - Example {i}: {exploit}")
            else:
                print(f"No exploits found for {banner}.")

        except Exception as e:
            print(f"Could not connect to {ip}:{port}")

        finally:
            sock.close()