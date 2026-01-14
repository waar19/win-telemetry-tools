"""
Network Monitor Module
Monitors active network connections and identifies potential telemetry traffic.
"""

import socket
import psutil
import threading
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

@dataclass
class NetworkConnection:
    pid: int
    process_name: str
    local_address: str
    remote_address: str
    status: str
    hostname: str = ""
    is_telemetry: bool = False


class NetworkMonitor:
    """Monitors system network connections."""
    
    # Known telemetry domains/IPs keywords
    TELEMETRY_KEYWORDS = [
        "telemetry", "vortex", "settings-win", "watson", "g.msn", 
        "adnxs", "doubleclick", "scorecardresearch", "adjust", "appsflyer"
    ]
    
    def __init__(self):
        self._dns_cache: Dict[str, str] = {}
        self._cache_lock = threading.Lock()
        self._resolver_pool = ThreadPoolExecutor(max_workers=5)
    
    def get_connections(self) -> List[NetworkConnection]:
        """Get list of current active network connections."""
        connections = []
        
        try:
            # Get all network connections
            for conn in psutil.net_connections(kind='inet'):
                if conn.status not in [psutil.CONN_ESTABLISHED, psutil.CONN_SYN_SENT]:
                    continue
                
                # Get process name
                try:
                    process = psutil.Process(conn.pid)
                    process_name = process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_name = "System/Unknown"
                
                # Get addresses
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
                
                if not raddr:
                    continue
                
                remote_ip = conn.raddr.ip
                
                # Resolve hostname (non-blocking if cached, otherwise submit task)
                hostname = self._get_hostname(remote_ip)
                
                is_telemetry = self._check_is_telemetry(hostname)
                
                connections.append(NetworkConnection(
                    conn.pid,
                    process_name,
                    laddr,
                    raddr,
                    conn.status,
                    hostname,
                    is_telemetry
                ))
                
        except Exception as e:
            print(f"Error getting connections: {e}")
            
        return sorted(connections, key=lambda x: x.is_telemetry, reverse=True)
    
    def _get_hostname(self, ip: str) -> str:
        """Get hostname for IP, using cache or starting resolution."""
        with self._cache_lock:
            if ip in self._dns_cache:
                return self._dns_cache[ip]
        
        # If not in cache, return IP temporarily and start resolution
        self._resolver_pool.submit(self._resolve_ip, ip)
        return ""
    
    def _resolve_ip(self, ip: str):
        """Resolve IP to hostname in background."""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
        except socket.herror:
            hostname = ip
        except Exception:
            hostname = ip
            
        with self._cache_lock:
            self._dns_cache[ip] = hostname
    
    def _check_is_telemetry(self, hostname: str) -> bool:
        """Check if hostname looks like telemetry."""
        if not hostname:
            return False
            
        hostname = hostname.lower()
        return any(keyword in hostname for keyword in self.TELEMETRY_KEYWORDS)
