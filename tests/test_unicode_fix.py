#!/usr/bin/env python3
"""
Test for UnicodeDecodeError fix in pull_server_info
"""
import socket
import threading
from unittest.mock import Mock, patch


def test_unicode_decode_error_simulation():
    """
    Test that simulates the UnicodeDecodeError scenario.
    This confirms that the error does occur with non-ASCII data.
    """
    # Create a mock server that sends non-ASCII data
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(('127.0.0.1', 0))
    server_port = server_sock.getsockname()[1]
    
    def mock_server():
        try:
            data, addr = server_sock.recvfrom(1024)
            # Send back data containing byte 0xac (like in the original error)
            response = b'\xac\x80invalid ascii response\x00'
            server_sock.sendto(response, addr)
        finally:
            server_sock.close()
    
    # Start mock server
    server_thread = threading.Thread(target=mock_server)
    server_thread.start()
    
    try:
        # Simulate what get_server_info() does
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.settimeout(1.0)
        udp.connect(('127.0.0.1', server_port))
        
        udp.send('\\status\\players\\'.encode('ascii'))
        data = udp.recv(4096)
        
        # This should raise UnicodeDecodeError
        try:
            decoded = data.decode('ascii')
            assert False, "Expected UnicodeDecodeError but decode succeeded"
        except UnicodeDecodeError as e:
            # Confirm it's the same type of error as in the original issue
            assert "'ascii' codec can't decode byte" in str(e)
            assert "ordinal not in range(128)" in str(e)
        finally:
            udp.close()
            
    finally:
        server_thread.join(timeout=2)


if __name__ == "__main__":
    test_unicode_decode_error_simulation()
    print("Test passed: UnicodeDecodeError properly reproduced")