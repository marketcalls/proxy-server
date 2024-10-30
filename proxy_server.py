#!/usr/bin/env python3
import socket
import threading
import logging
import argparse
from urllib.parse import urlparse
from logging.handlers import RotatingFileHandler
import os
import sys
import select
import time
import ssl

class ProxyServer:
    def __init__(self, host='0.0.0.0', port=8080, buffer_size=8192, log_dir="logs"):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server_socket = None
        
        # Set up logging
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                RotatingFileHandler(
                    os.path.join(log_dir, 'proxy.log'),
                    maxBytes=10*1024*1024,
                    backupCount=5
                ),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('proxy')

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Increase socket buffer size
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            self.logger.info(f"Proxy server started on {self.host}:{self.port}")
            
            while True:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self.logger.info(f"Accepted connection from {client_address[0]}")
                    proxy_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    proxy_thread.daemon = True
                    proxy_thread.start()
                except Exception as e:
                    self.logger.error(f"Error accepting connection: {e}")
                    continue
                
        except Exception as e:
            self.logger.error(f"Error starting proxy server: {e}")
            self.stop()

    def handle_client(self, client_socket, client_address):
        try:
            request = b""
            while True:
                try:
                    chunk = client_socket.recv(self.buffer_size)
                    if not chunk:
                        break
                    request += chunk
                    if b"\r\n\r\n" in request:
                        break
                except socket.timeout:
                    break

            if not request:
                return

            self.logger.debug(f"Raw request from {client_address[0]}:\n{request.decode('utf-8', errors='ignore')}")

            first_line = request.split(b"\r\n")[0].decode('utf-8')
            self.logger.info(f"First line: {first_line}")
            
            method, url, protocol = first_line.split()
            
            if method == 'CONNECT':
                self.handle_https_tunnel(client_socket, url, client_address[0])
            else:
                self.handle_http_request(client_socket, request, method, url, protocol, client_address[0])

        except Exception as e:
            self.logger.error(f"Error handling client {client_address[0]}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def handle_https_tunnel(self, client_socket, url, client_ip):
        server_socket = None
        try:
            hostname, port = url.split(':')
            port = int(port)
            
            self.logger.info(f"Setting up HTTPS tunnel to {hostname}:{port}")
            
            # Create connection to destination server
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            
            try:
                server_socket.connect((hostname, port))
                response = "HTTP/1.1 200 Connection established\r\n\r\n"
                client_socket.sendall(response.encode())
                self.logger.info(f"HTTPS tunnel established for {client_ip} to {hostname}:{port}")
            except Exception as e:
                self.logger.error(f"Failed to connect to destination {hostname}:{port} - {e}")
                response = "HTTP/1.1 502 Bad Gateway\r\n\r\n"
                client_socket.sendall(response.encode())
                return

            # Create bidirectional tunnel
            self.tunnel_traffic(client_socket, server_socket, hostname)

        except Exception as e:
            self.logger.error(f"Error in HTTPS tunneling: {e}")
        finally:
            if server_socket:
                try:
                    server_socket.close()
                except:
                    pass

    def tunnel_traffic(self, client_socket, server_socket, hostname):
        def forward(source, destination, direction):
            try:
                while True:
                    try:
                        data = source.recv(self.buffer_size)
                        if not data:
                            break
                        destination.sendall(data)
                        self.logger.debug(f"Forwarded {len(data)} bytes {direction} for {hostname}")
                    except (socket.error, ConnectionResetError) as e:
                        self.logger.error(f"Connection error while forwarding {direction}: {e}")
                        break
                    except Exception as e:
                        self.logger.error(f"Error forwarding {direction}: {e}")
                        break
            finally:
                try:
                    source.shutdown(socket.SHUT_RDWR)
                    source.close()
                except:
                    pass
                try:
                    destination.shutdown(socket.SHUT_RDWR)
                    destination.close()
                except:
                    pass

        # Start bidirectional forwarding
        client_to_server = threading.Thread(
            target=forward,
            args=(client_socket, server_socket, "→"),
            daemon=True
        )
        server_to_client = threading.Thread(
            target=forward,
            args=(server_socket, client_socket, "←"),
            daemon=True
        )
        
        client_to_server.start()
        server_to_client.start()
        
        # Wait for both directions to complete
        client_to_server.join()
        server_to_client.join()

    def handle_http_request(self, client_socket, request, method, url, protocol, client_ip):
        server_socket = None
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.netloc
            
            if not hostname:
                for line in request.split(b"\r\n"):
                    if line.startswith(b"Host: "):
                        hostname = line[6:].strip().decode('utf-8')
                        break

            self.logger.info(f"HTTP request: {method} {hostname}{parsed_url.path}")
            
            port = parsed_url.port or 80
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            server_socket.connect((hostname.split(':')[0], port))

            # Forward the modified request
            if parsed_url.netloc:
                modified_request = request.replace(url.encode(), parsed_url.path.encode() or b'/')
                server_socket.sendall(modified_request)
            else:
                server_socket.sendall(request)

            # Create tunnel for the response
            self.tunnel_traffic(client_socket, server_socket, hostname)

        except Exception as e:
            self.logger.error(f"Error in HTTP request handling: {e}")
        finally:
            if server_socket:
                try:
                    server_socket.close()
                except:
                    pass

def main():
    parser = argparse.ArgumentParser(description='Enhanced SSL Proxy Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--buffer-size', type=int, default=8192, help='Buffer size')
    parser.add_argument('--log-dir', default='logs', help='Directory for log files')
    
    args = parser.parse_args()
    
    proxy = ProxyServer(args.host, args.port, args.buffer_size, args.log_dir)
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.logger.info("Shutting down proxy server...")
        proxy.stop()

if __name__ == "__main__":
    main()
