"""
Firewall Manager Module
Manages Windows Firewall rules to block Microsoft telemetry endpoints.
"""

import subprocess
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class FirewallRule:
    """Represents a firewall rule."""
    name: str
    description: str
    remote_addresses: List[str]
    is_active: bool = False
    direction: str = "Out"  # Out or In


@dataclass
class TelemetryEndpoint:
    """Represents a telemetry endpoint to block."""
    domain: str
    description: str
    category: str
    ip_addresses: List[str]


class FirewallManager:
    """Manages Windows Firewall rules for blocking telemetry."""
    
    RULE_PREFIX = "PrivacyDashboard_Block_"
    
    # Microsoft telemetry endpoints to block
    TELEMETRY_ENDPOINTS = [
        TelemetryEndpoint(
            domain="telemetry.microsoft.com",
            description="Main Microsoft telemetry endpoint",
            category="Telemetry",
            ip_addresses=["13.107.5.88", "13.107.4.52"]
        ),
        TelemetryEndpoint(
            domain="vortex.data.microsoft.com",
            description="Windows telemetry data collection",
            category="Telemetry",
            ip_addresses=["13.107.5.88"]
        ),
        TelemetryEndpoint(
            domain="vortex-win.data.microsoft.com",
            description="Windows telemetry data collection",
            category="Telemetry",
            ip_addresses=["13.107.5.88"]
        ),
        TelemetryEndpoint(
            domain="settings-win.data.microsoft.com",
            description="Windows settings sync",
            category="Telemetry",
            ip_addresses=["13.107.5.88"]
        ),
        TelemetryEndpoint(
            domain="watson.telemetry.microsoft.com",
            description="Error reporting telemetry",
            category="Error Reporting",
            ip_addresses=["65.55.252.93"]
        ),
        TelemetryEndpoint(
            domain="watson.microsoft.com",
            description="Watson error reporting",
            category="Error Reporting",
            ip_addresses=["65.55.252.71"]
        ),
        TelemetryEndpoint(
            domain="oca.telemetry.microsoft.com",
            description="Online Crash Analysis",
            category="Error Reporting",
            ip_addresses=["65.55.252.63"]
        ),
        TelemetryEndpoint(
            domain="sqm.telemetry.microsoft.com",
            description="Software Quality Metrics",
            category="Telemetry",
            ip_addresses=["65.55.252.93"]
        ),
        TelemetryEndpoint(
            domain="feedback.microsoft.com",
            description="Feedback Hub",
            category="Feedback",
            ip_addresses=["13.107.6.158"]
        ),
        TelemetryEndpoint(
            domain="feedback.windows.com",
            description="Windows Feedback",
            category="Feedback",
            ip_addresses=["13.107.6.158"]
        ),
        TelemetryEndpoint(
            domain="diagnostics.support.microsoft.com",
            description="Diagnostics support",
            category="Diagnostics",
            ip_addresses=["13.107.21.200"]
        ),
        TelemetryEndpoint(
            domain="corp.sts.microsoft.com",
            description="Corporate telemetry",
            category="Telemetry",
            ip_addresses=["13.107.6.171"]
        ),
        TelemetryEndpoint(
            domain="statsfe2.ws.microsoft.com",
            description="Statistics endpoint",
            category="Statistics",
            ip_addresses=["13.107.4.52"]
        ),
        TelemetryEndpoint(
            domain="i1.services.social.microsoft.com",
            description="Social services telemetry",
            category="Social",
            ip_addresses=["13.107.6.158"]
        ),
        TelemetryEndpoint(
            domain="redir.metaservices.microsoft.com",
            description="Metaservices redirect",
            category="Telemetry",
            ip_addresses=["13.107.4.52"]
        ),
        TelemetryEndpoint(
            domain="choice.microsoft.com",
            description="Choice settings",
            category="Telemetry",
            ip_addresses=["13.107.4.50"]
        ),
        TelemetryEndpoint(
            domain="df.telemetry.microsoft.com",
            description="Data forwarding telemetry",
            category="Telemetry",
            ip_addresses=["13.107.5.88"]
        ),
        TelemetryEndpoint(
            domain="reports.wes.df.telemetry.microsoft.com",
            description="Telemetry reports",
            category="Telemetry",
            ip_addresses=["13.107.5.88"]
        ),
        TelemetryEndpoint(
            domain="wes.df.telemetry.microsoft.com",
            description="WES telemetry",
            category="Telemetry",
            ip_addresses=["13.107.5.88"]
        ),
        TelemetryEndpoint(
            domain="services.wes.df.telemetry.microsoft.com",
            description="WES telemetry services",
            category="Telemetry",
            ip_addresses=["13.107.5.88"]
        ),
        TelemetryEndpoint(
            domain="sqm.df.telemetry.microsoft.com",
            description="SQM telemetry",
            category="Telemetry",
            ip_addresses=["13.107.5.88"]
        ),
        TelemetryEndpoint(
            domain="activity.windows.com",
            description="Windows Activity tracking",
            category="Activity",
            ip_addresses=["13.107.6.158"]
        ),
        TelemetryEndpoint(
            domain="bingapis.com",
            description="Bing APIs",
            category="Advertising",
            ip_addresses=["13.107.21.200"]
        ),
    ]
    
    def __init__(self):
        self._cache: Dict[str, bool] = {}
    
    def get_all_rules_status(self) -> List[FirewallRule]:
        """Get status of all telemetry blocking rules."""
        rules = []
        
        for endpoint in self.TELEMETRY_ENDPOINTS:
            rule_name = f"{self.RULE_PREFIX}{endpoint.domain.replace('.', '_')}"
            is_active = self._check_rule_exists(rule_name)
            
            rules.append(FirewallRule(
                name=endpoint.domain,
                description=endpoint.description,
                remote_addresses=endpoint.ip_addresses,
                is_active=is_active,
                direction="Out"
            ))
        
        return rules
    
    def get_blocked_count(self) -> Tuple[int, int]:
        """Get count of blocked endpoints vs total."""
        rules = self.get_all_rules_status()
        blocked = sum(1 for r in rules if r.is_active)
        return blocked, len(rules)
    
    def get_privacy_score(self) -> int:
        """Calculate privacy score based on blocked endpoints (0-100)."""
        blocked, total = self.get_blocked_count()
        if total == 0:
            return 0
        return int((blocked / total) * 100)
    
    def block_endpoint(self, endpoint: TelemetryEndpoint) -> Tuple[bool, str]:
        """Create firewall rule to block an endpoint."""
        rule_name = f"{self.RULE_PREFIX}{endpoint.domain.replace('.', '_')}"
        
        # Create outbound blocking rule
        try:
            # Build the netsh command
            cmd = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name={rule_name}",
                "dir=out",
                "action=block",
                f"remoteip={','.join(endpoint.ip_addresses)}",
                f"description=Privacy Dashboard: Block {endpoint.description}",
                "enable=yes"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 or "already exists" in result.stderr.lower():
                return True, f"Blocked {endpoint.domain}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def unblock_endpoint(self, endpoint: TelemetryEndpoint) -> Tuple[bool, str]:
        """Remove firewall rule for an endpoint."""
        rule_name = f"{self.RULE_PREFIX}{endpoint.domain.replace('.', '_')}"
        
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 or "no rules" in result.stdout.lower():
                return True, f"Unblocked {endpoint.domain}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def block_all_telemetry(self, progress_callback=None) -> Tuple[bool, str]:
        """Block all telemetry endpoints."""
        errors = []
        total = len(self.TELEMETRY_ENDPOINTS)
        
        for i, endpoint in enumerate(self.TELEMETRY_ENDPOINTS):
            if progress_callback:
                progress_callback(i + 1, total, endpoint.domain)
            
            success, error = self.block_endpoint(endpoint)
            if not success:
                errors.append(f"{endpoint.domain}: {error}")
        
        if errors:
            return False, f"Some endpoints failed:\n" + "\n".join(errors[:5])
        return True, f"Blocked {total} telemetry endpoints"
    
    def unblock_all_telemetry(self, progress_callback=None) -> Tuple[bool, str]:
        """Remove all telemetry blocking rules."""
        errors = []
        total = len(self.TELEMETRY_ENDPOINTS)
        
        for i, endpoint in enumerate(self.TELEMETRY_ENDPOINTS):
            if progress_callback:
                progress_callback(i + 1, total, endpoint.domain)
            
            success, error = self.unblock_endpoint(endpoint)
            if not success:
                errors.append(f"{endpoint.domain}: {error}")
        
        if errors:
            return False, f"Some endpoints failed:\n" + "\n".join(errors[:5])
        return True, f"Unblocked {total} telemetry endpoints"
    
    def block_by_category(self, category: str) -> Tuple[bool, str]:
        """Block all endpoints in a category."""
        errors = []
        count = 0
        
        for endpoint in self.TELEMETRY_ENDPOINTS:
            if endpoint.category == category:
                success, error = self.block_endpoint(endpoint)
                if success:
                    count += 1
                else:
                    errors.append(error)
        
        if errors:
            return False, f"Blocked {count} endpoints, {len(errors)} failed"
        return True, f"Blocked {count} {category} endpoints"
    
    def get_categories(self) -> List[str]:
        """Get list of endpoint categories."""
        categories = set()
        for endpoint in self.TELEMETRY_ENDPOINTS:
            categories.add(endpoint.category)
        return sorted(list(categories))
    
    def get_endpoints_by_category(self, category: str) -> List[TelemetryEndpoint]:
        """Get endpoints in a specific category."""
        return [e for e in self.TELEMETRY_ENDPOINTS if e.category == category]
    
    def _check_rule_exists(self, rule_name: str) -> bool:
        """Check if a firewall rule exists."""
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "firewall", "show", "rule", f"name={rule_name}"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "No rules match" not in result.stdout and result.returncode == 0
        except Exception:
            return False
    
    def check_admin_rights(self) -> bool:
        """Check if running with admin rights."""
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "currentprofile"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def export_rules(self, filepath: str) -> Tuple[bool, str]:
        """Export current firewall rules to a file."""
        try:
            result = subprocess.run(
                ["netsh", "advfirewall", "export", filepath],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                return True, f"Rules exported to {filepath}"
            return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def add_hosts_block(self) -> Tuple[bool, str]:
        """Add telemetry domains to hosts file for additional blocking."""
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        marker_start = "# PrivacyDashboard Telemetry Block Start"
        marker_end = "# PrivacyDashboard Telemetry Block End"
        
        try:
            # Read existing hosts file
            with open(hosts_path, 'r') as f:
                content = f.read()
            
            # Remove existing blocks
            if marker_start in content:
                start_idx = content.find(marker_start)
                end_idx = content.find(marker_end)
                if end_idx != -1:
                    content = content[:start_idx] + content[end_idx + len(marker_end):]
            
            # Build new block
            block_lines = ["\n" + marker_start]
            for endpoint in self.TELEMETRY_ENDPOINTS:
                block_lines.append(f"0.0.0.0 {endpoint.domain}")
            block_lines.append(marker_end + "\n")
            
            # Write updated hosts file
            with open(hosts_path, 'w') as f:
                f.write(content.strip() + "\n" + "\n".join(block_lines))
            
            return True, f"Added {len(self.TELEMETRY_ENDPOINTS)} domains to hosts file"
        except Exception as e:
            return False, str(e)
    
    def remove_hosts_block(self) -> Tuple[bool, str]:
        """Remove telemetry domains from hosts file."""
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        marker_start = "# PrivacyDashboard Telemetry Block Start"
        marker_end = "# PrivacyDashboard Telemetry Block End"
        
        try:
            with open(hosts_path, 'r') as f:
                content = f.read()
            
            if marker_start in content:
                start_idx = content.find(marker_start)
                end_idx = content.find(marker_end)
                if end_idx != -1:
                    content = content[:start_idx] + content[end_idx + len(marker_end):]
                    
                    with open(hosts_path, 'w') as f:
                        f.write(content.strip() + "\n")
                    
                    return True, "Removed telemetry blocks from hosts file"
            
            return True, "No blocks found in hosts file"
        except Exception as e:
            return False, str(e)
