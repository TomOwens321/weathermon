"""Utilities for receiving JSON payloads over UDP."""

import json
import socket


def listen_udp_json(port, host="0.0.0.0", bufsize=65535, timeout=None):
    """Listen for UDP datagrams and yield valid JSON strings.

    Binds a UDP socket to ``(host, port)`` and yields the decoded text of any
    datagram whose contents are valid JSON. Invalid JSON datagrams are ignored.

    Args:
        port: UDP port number to bind to.
        host: Local address to bind to. Defaults to all interfaces.
        bufsize: Maximum datagram size to read at once.
        timeout: Optional socket timeout in seconds. ``None`` blocks indefinitely.

    Yields:
        str: Each received datagram payload that parses as valid JSON, decoded
        as UTF-8 text (with replacement for invalid byte sequences).
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if timeout is not None:
        sock.settimeout(timeout)
    sock.bind((host, port))
    try:
        while True:
            try:
                data, _addr = sock.recvfrom(bufsize)
            except socket.timeout:
                return
            try:
                text = data.decode("utf-8", errors="replace")
                json.loads(text)
            except (ValueError, TypeError):
                continue
            yield text
    finally:
        sock.close()
