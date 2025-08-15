import asyncio
import socket
import platform
import subprocess
from typing import List, Tuple

async def tcp_connect(host: str, port: int, timeout: float = 2.0) -> bool:
    """
    Try to connect to a TCP port asynchronously.
    """
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

def ping_host(host: str) -> bool:
    """
    Check if host responds to ICMP ping.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    cmd = ["ping", param, "1", host]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        return True
    except:
        return False

async def scan_ports(host: str, ports: List[int], timeout: float = 2.0) -> List[int]:
    """
    Scan given ports on host and return list of open ports.
    """
    open_ports = []
    tasks = [tcp_connect(host, port, timeout) for port in ports]
    results = await asyncio.gather(*tasks)
    for port, status in zip(ports, results):
        if status:
            open_ports.append(port)
    return open_ports

def verify_subdomains(subdomains: List[str], method: str, ports: List[int], concurrency: int) -> List[Tuple[str, bool, List[int]]]:
    """
    Verify subdomains based on method and return a list of (subdomain, alive?, open_ports).
    """
    results = []

    async def worker(sub: str):
        if method == "ping":
            alive = ping_host(sub)
            return (sub, alive, [])
        else:
            alive_ports = await scan_ports(sub, ports)
            alive = len(alive_ports) > 0
            return (sub, alive, alive_ports)

    async def run_all():
        sem = asyncio.Semaphore(concurrency)
        async def sem_task(sub):
            async with sem:
                return await worker(sub)
        return await asyncio.gather(*(sem_task(s) for s in subdomains))

    results = asyncio.run(run_all())
    return results
