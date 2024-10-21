#!/usr/bin/env python3
import os
import time
import yaml
import logging
import requests
import threading
from datetime import datetime, timedelta
from collections import defaultdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# =======================
# Configuration Management
# =======================

def load_config(config_path="/usr/local/opnsense/mvc/app/plugins/smt/etc/opnsense/scripts/smt/config.yaml"):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# =======================
# Logging Setup
# =======================

logging.basicConfig(
    level=getattr(logging, config['logging']['level'].upper(), logging.INFO),
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(config['logging']['file']),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# =======================
# Blocklist Management
# =======================

class BlocklistManager:
    def __init__(self, repo_url, local_path):
        self.repo_url = repo_url
        self.local_path = local_path
        self.domains = set()
        self.load_blocklist()

    def load_blocklist(self):
        # For simplicity, assume the blocklist is a raw text file with one domain per line
        try:
            if not os.path.exists(self.local_path):
                self.fetch_blocklist()
            with open(self.local_path, 'r') as f:
                for line in f:
                    domain = line.strip()
                    if domain and not domain.startswith('#'):
                        self.domains.add(domain.lower())
            logger.info(f"Loaded {len(self.domains)} domains from blocklist.")
        except Exception as e:
            logger.error(f"Failed to load blocklist: {e}")

    def fetch_blocklist(self):
        # Clone or pull the latest blocklist from GitHub
        # For simplicity, assume the blocklist is a single file
        try:
            raw_url = self.repo_url.replace("github.com", "raw.githubusercontent.com") + "/master/social_media_domains.txt"
            response = requests.get(raw_url, verify=False)
            response.raise_for_status()
            os.makedirs(os.path.dirname(self.local_path), exist_ok=True)
            with open(self.local_path, 'w') as f:
                f.write(response.text)
            logger.info("Fetched latest blocklist from GitHub.")
        except requests.RequestException as e:
            logger.error(f"Failed to fetch blocklist from GitHub: {e}")

    def is_social_media_domain(self, domain):
        return domain.lower() in self.domains

# =======================
# State Management
# =======================

class StateManager:
    def __init__(self, state_file="state.yaml"):
        self.state_file = state_file
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.state = yaml.safe_load(f) or {}
        else:
            self.state = {}
        # Initialize structures
        self.state.setdefault('usage', defaultdict(list))  # user_ip -> list of access times
        self.state.setdefault('blocked', {})  # user_ip -> unblock_time
        logger.debug("State loaded.")

    def save_state(self):
        with open(self.state_file, 'w') as f:
            yaml.dump(self.state, f)
        logger.debug("State saved.")

    def add_access_time(self, user_ip, access_time):
        self.state['usage'][user_ip].append(access_time)
        logger.debug(f"Added access time for {user_ip}: {access_time}")

    def get_usage_times(self, user_ip):
        return self.state['usage'].get(user_ip, [])

    def block_user(self, user_ip, unblock_time):
        self.state['blocked'][user_ip] = unblock_time
        logger.info(f"User {user_ip} blocked until {unblock_time}.")
    
    def unblock_user(self, user_ip):
        if user_ip in self.state['blocked']:
            del self.state['blocked'][user_ip]
            logger.info(f"User {user_ip} unblocked.")

    def is_blocked(self, user_ip):
        unblock_time = self.state['blocked'].get(user_ip)
        if unblock_time:
            if datetime.now() >= unblock_time:
                self.unblock_user(user_ip)
                return False
            else:
                return True
        return False

# =======================
# RPZ (Response Policy Zone) Management
# =======================

class RPZManager:
    def __init__(self, rpz_file, opnsense_reload_command):
        self.rpz_file = rpz_file
        self.opnsense_reload_command = opnsense_reload_command
        self.blocked_ips = {}  # user_ip -> unblock_time
        self.lock = threading.Lock()
        self.ensure_rpz_file()

    def ensure_rpz_file(self):
        if not os.path.exists(self.rpz_file):
            os.makedirs(os.path.dirname(self.rpz_file), exist_ok=True)
            with open(self.rpz_file, 'w') as f:
                f.write("# RPZ for Social Media Timeout Plugin\n")
            logger.info(f"Created RPZ file at {self.rpz_file}.")
    
    def add_block(self, user_ip, block_duration, blocklist_manager):
        with self.lock:
            if user_ip not in self.blocked_ips:
                # Add social media domains to RPZ
                with open(self.rpz_file, 'a') as f:
                    for domain in blocklist_manager.domains:
                        f.write(f"{domain} CNAME blocked.\n")
                self.blocked_ips[user_ip] = datetime.now() + block_duration
                logger.info(f"Added block for {user_ip}.")
                self.reload_unbound()

    def remove_block(self, user_ip, blocklist_manager):
        with self.lock:
            if user_ip in self.blocked_ips:
                # Remove social media domains from RPZ
                if os.path.exists(self.rpz_file):
                    with open(self.rpz_file, 'r') as f:
                        lines = f.readlines()
                    with open(self.rpz_file, 'w') as f:
                        for line in lines:
                            if not any(domain in line for domain in blocklist_manager.domains):
                                f.write(line)
                del self.blocked_ips[user_ip]
                logger.info(f"Removed block for {user_ip}.")
                self.reload_unbound()

    def reload_unbound(self):
        try:
            os.system(self.opnsense_reload_command)
            logger.info("Unbound DNS reloaded.")
        except Exception as e:
            logger.error(f"Failed to reload Unbound DNS: {e}")

    def manage_blocks(self, blocklist_manager):
        while True:
            now = datetime.now()
            with self.lock:
                to_unblock = [ip for ip, unblock_time in self.blocked_ips.items() if now >= unblock_time]
                for ip in to_unblock:
                    self.remove_block(ip, blocklist_manager)
            time.sleep(60)  # Check every minute

# =======================
# Log File Handler
# =======================

class LogHandler(FileSystemEventHandler):
    def __init__(self, log_file, callback):
        super().__init__()
        self.log_file = log_file
        self.callback = callback
        self._position = 0
        self._lock = threading.Lock()
        self._open_log_file()

    def _open_log_file(self):
        self.file = open(self.log_file, 'r')
        self.file.seek(0, os.SEEK_END)
        self._position = self.file.tell()
        logger.debug(f"Opened log file {self.log_file} at position {self._position}.")
    
    def on_modified(self, event):
        if event.src_path == self.log_file:
            with self._lock:
                self.file.seek(self._position)
                lines = self.file.readlines()
                self._position = self.file.tell()
                if lines:
                    self.callback(lines)

    def on_moved(self, event):
        if event.src_path == self.log_file:
            logger.info(f"Log file {self.log_file} moved to {event.dest_path}. Re-opening.")
            self.file.close()
            time.sleep(1)  # Wait for the new log file to be created
            self._open_log_file()

    def on_deleted(self, event):
        if event.src_path == self.log_file:
            logger.warning(f"Log file {self.log_file} deleted.")
            self.file.close()

# =======================
# SMT Plugin Core
# =======================

class SMTPlugin:
    def __init__(self, config):
        self.config = config
        self.blocklist_manager = BlocklistManager(
            repo_url=config['blocklist']['repo_url'],
            local_path=config['blocklist']['local_path']
        )
        self.state = StateManager(state_file="/usr/local/opnsense/mvc/app/plugins/smt/etc/opnsense/scripts/smt/state.yaml")
        self.usage_threshold = timedelta(hours=config['social_media']['usage_threshold_hours'])
        self.block_duration = timedelta(minutes=config['social_media']['block_duration_minutes'])
        self.unbound_log = config['unbound']['log_file']
        self.rpz_file = config['unbound']['rpz_file']
        self.rpz_manager = RPZManager(
            rpz_file=self.rpz_file,
            opnsense_reload_command=config['opnsense']['unbound_reload_command']
        )
        self.observer = Observer()
        self.setup_log_handler()
        self.setup_rpz_manager()

    def setup_log_handler(self):
        event_handler = LogHandler(self.unbound_log, self.process_log_lines)
        self.observer.schedule(event_handler, path=os.path.dirname(self.unbound_log) or '.', recursive=False)
        self.observer.start()
        logger.info("Started log file observer.")

    def setup_rpz_manager(self):
        unblock_thread = threading.Thread(target=self.rpz_manager.manage_blocks, args=(self.blocklist_manager,), daemon=True)
        unblock_thread.start()
        logger.info("Started RPZ block management thread.")

    def process_log_lines(self, lines):
        for line in lines:
            domain = self.extract_domain(line)
            user_ip = self.extract_ip(line)
            if domain and user_ip and self.blocklist_manager.is_social_media_domain(domain):
                access_time = datetime.now()
                self.state.add_access_time(user_ip, access_time)
                logger.debug(f"Detected social media access by {user_ip} to {domain} at {access_time}.")
                self.check_and_block(user_ip)

    def extract_domain(self, log_line):
        # Adjust this method based on actual Unbound log format
        # Example log line: "[2024-10-21 12:34:56] client 192.168.1.100 query: facebook.com IN A +"
        try:
            parts = log_line.split()
            if 'query:' in parts:
                query_index = parts.index('query:') + 1
                domain = parts[query_index].split('.')[0]  # Extract the main domain
                return domain.lower()
        except Exception as e:
            logger.error(f"Failed to extract domain from log line: {e}")
        return None

    def extract_ip(self, log_line):
        # Adjust this method based on actual Unbound log format
        try:
            parts = log_line.split()
            if 'client' in parts:
                client_index = parts.index('client') + 1
                return parts[client_index]
        except Exception as e:
            logger.error(f"Failed to extract IP from log line: {e}")
        return None

    def check_and_block(self, user_ip):
        if self.state.is_blocked(user_ip):
            logger.debug(f"User {user_ip} is already blocked.")
            return

        access_times = self.state.get_usage_times(user_ip)
        if not access_times:
            return

        # Calculate usage within the threshold period
        cutoff_time = datetime.now() - self.usage_threshold
        recent_access = [t for t in access_times if t >= cutoff_time]
        usage_count = len(recent_access)

        # Example: Threshold is usage_threshold_hours * 60 accesses (assuming one access per minute)
        required_access = int(self.usage_threshold.total_seconds() / 60)

        if usage_count >= required_access:
            self.block_user(user_ip)

    def block_user(self, user_ip):
        if not self.state.is_blocked(user_ip):
            self.rpz_manager.add_block(user_ip, self.block_duration, self.blocklist_manager)
            unblock_time = datetime.now() + self.block_duration
            self.state.block_user(user_ip, unblock_time)
            self.state.save_state()
            logger.info(f"User {user_ip} has been blocked from accessing social media.")

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down SMT Plugin.")
            self.observer.stop()
        self.observer.join()

# =======================
# Main Execution
# =======================

if __name__ == "__main__":
    plugin = SMTPlugin(config)
    plugin.run()

