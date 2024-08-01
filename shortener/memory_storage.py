import threading
import time
from datetime import datetime
import random, string

class MemoryStorage:
    def __init__(self):
        self.url_mapping = {}
        self.access_logs = {}
        self.ttl_info = {}
        self.lock = threading.Lock()
        self.cleanup_thread = threading.Thread(target=self.cleanup_expired_urls, daemon=True)
        self.cleanup_thread.start()

    def generate_random_alias(self):
        
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    def cleanup_expired_urls(self):
        while True:
            time.sleep(1) 
            with self.lock:
                now = datetime.now()
                expired_aliases = [alias for alias, ttl in self.ttl_info.items() if ttl < now]
                for alias in expired_aliases:
                    del self.url_mapping[alias]
                    del self.ttl_info[alias]
                    if alias in self.access_logs:
                        del self.access_logs[alias]


