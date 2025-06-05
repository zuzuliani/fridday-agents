import redis
import json
from ..config import settings
from typing import Any, Dict, Optional

class RedisMemory:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    def set_memory(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Store a value in Redis memory
        """
        try:
            serialized_value = json.dumps(value)
            self.redis_client.set(key, serialized_value)
            if expire:
                self.redis_client.expire(key, expire)
            return True
        except Exception as e:
            print(f"Error setting memory: {e}")
            return False
    
    def get_memory(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from Redis memory
        """
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error getting memory: {e}")
            return None
    
    def delete_memory(self, key: str) -> bool:
        """
        Delete a value from Redis memory
        """
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
    
    def clear_all_memories(self) -> bool:
        """
        Clear all memories (use with caution)
        """
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Error clearing memories: {e}")
            return False

# Create a singleton instance
memory = RedisMemory() 