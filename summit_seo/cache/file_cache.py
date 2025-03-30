"""File-based cache implementation."""

import asyncio
import json
import os
import pickle
import hashlib
import tempfile
import fnmatch
import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union, Set

from .base import BaseCache, CacheConfig, CacheError, CacheKeyError, CacheResult, CacheValueError, CacheKey

# Type variables for key and value
K = TypeVar('K')
V = TypeVar('V')

class FileCacheError(CacheError):
    """Exception raised for file cache-specific errors."""
    pass


class FileCache(BaseCache[CacheKey, Any]):
    """File-based cache implementation.
    
    This cache stores items in files on disk for persistence between
    application runs.
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize the file cache.
        
        Args:
            config: Optional cache configuration. In addition to standard CacheConfig,
                   supports 'cache_dir' parameter.
        """
        super().__init__(config)
        
        # Get cache directory from config or use temp directory
        self._cache_dir = self.config.metadata.get('cache_dir') if hasattr(self.config, 'metadata') else None
        if not self._cache_dir:
            self._cache_dir = os.path.join(tempfile.gettempdir(), 'summit_seo_cache')
            
        # Create cache directory if it doesn't exist
        os.makedirs(self._cache_dir, exist_ok=True)
        
        # Create namespace directory
        self._ensure_namespace(self.config.namespace)
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
        
        # Internal key registry to avoid file system lookups
        self._registry: Dict[str, Set[str]] = {}
    
    def _ensure_namespace(self, namespace: str) -> None:
        """Ensure namespace directory exists.
        
        Args:
            namespace: Namespace to ensure exists
        """
        ns_dir = os.path.join(self._cache_dir, namespace)
        os.makedirs(ns_dir, exist_ok=True)
        
        # Initialize registry for this namespace
        if namespace not in self._registry:
            self._registry[namespace] = set()
            
            # Load existing keys from directory
            try:
                for filename in os.listdir(ns_dir):
                    if filename.endswith('.cache'):
                        key = self._filename_to_key(filename)
                        self._registry[namespace].add(key)
            except (OSError, IOError) as e:
                raise FileCacheError(f"Error accessing cache directory: {str(e)}")
    
    def _get_file_path(self, key: CacheKey, namespace: Optional[str] = None) -> str:
        """Get the file path for a cache key.
        
        Args:
            key: Cache key
            namespace: Optional namespace (defaults to config namespace)
            
        Returns:
            File path for the key
        """
        ns = namespace or self.config.namespace
        key_hash = self._key_to_filename(key)
        return os.path.join(self._cache_dir, ns, key_hash)
    
    def _key_to_filename(self, key: CacheKey) -> str:
        """Convert a cache key to a valid filename.
        
        Args:
            key: Cache key
            
        Returns:
            Valid filename for the key
        """
        if isinstance(key, str):
            key_str = key
        elif isinstance(key, tuple):
            key_str = '_'.join(str(item) for item in key)
        else:
            key_str = str(key)
        
        # Hash the key to get a safe filename
        key_hash = hashlib.md5(key_str.encode('utf-8')).hexdigest()
        return f"{key_hash}.cache"
    
    def _filename_to_key(self, filename: str) -> str:
        """Extract a key hash from a filename.
        
        Args:
            filename: Cache filename
            
        Returns:
            Key hash
        """
        return filename[:-6]  # Remove '.cache' suffix
    
    async def get(self, key: CacheKey) -> CacheResult[Any]:
        """Get a value from the cache.
        
        Args:
            key: The cache key to retrieve
            
        Returns:
            CacheResult containing the value and hit status
            
        Raises:
            CacheKeyError: If the key is invalid
            FileCacheError: If there's an error reading the cache file
        """
        if key is None:
            self._update_stats(miss=True)
            raise CacheKeyError("Cache key cannot be None")
        
        file_path = self._get_file_path(key)
        
        # If the file doesn't exist, return a cache miss
        if not os.path.exists(file_path):
            self._update_stats(miss=True)
            return CacheResult(
                value=None,
                hit=False,
                timestamp=datetime.now(),
                ttl=self.config.ttl,
                expired=False
            )
        
        try:
            # Load metadata and check expiration
            async with self._lock:
                with open(file_path, 'rb') as f:
                    entry = pickle.load(f)
                
                # Check if entry has expired
                now = datetime.now().timestamp()
                expiration_time = entry['timestamp'] + entry['ttl']
                
                if entry['ttl'] > 0 and now > expiration_time:
                    # Remove expired entry
                    os.remove(file_path)
                    key_hash = self._key_to_filename(key)
                    self._registry[self.config.namespace].discard(key_hash[:-6])
                    self._update_stats(miss=True)
                    
                    return CacheResult(
                        value=None,
                        hit=False,
                        timestamp=datetime.fromtimestamp(entry['timestamp']),
                        ttl=entry['ttl'],
                        expired=True
                    )
                
                # Update access time
                entry['last_accessed'] = now
                entry['access_count'] += 1
                
                # Write updated metadata back to file
                with open(file_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                self._update_stats(hit=True)
                return CacheResult(
                    value=entry['value'],
                    hit=True,
                    timestamp=datetime.fromtimestamp(entry['timestamp']),
                    ttl=entry['ttl'],
                    expired=False,
                    metadata={
                        'access_count': entry['access_count'],
                        'last_accessed': datetime.fromtimestamp(entry['last_accessed'])
                    }
                )
                
        except (OSError, IOError, pickle.PickleError) as e:
            self._update_stats(error=True)
            raise FileCacheError(f"Error reading cache file: {str(e)}")
    
    async def set(self, key: CacheKey, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: The cache key to set
            value: The value to cache
            ttl: Optional time to live in seconds (overrides config.ttl if provided)
            
        Raises:
            CacheKeyError: If the key is invalid
            CacheValueError: If the value is None
            FileCacheError: If there's an error writing the cache file
        """
        if key is None:
            self._update_stats(error=True)
            raise CacheKeyError("Cache key cannot be None")
        
        if value is None:
            self._update_stats(error=True)
            raise CacheValueError("Cache value cannot be None")
        
        ttl_value = ttl if ttl is not None else self.config.ttl
        file_path = self._get_file_path(key)
        
        # Check if we need to evict items to maintain max_size
        async with self._lock:
            if len(self._registry[self.config.namespace]) >= self.config.max_size:
                await self._evict_items()
            
            # Create cache entry
            entry = {
                'key': key,
                'value': value,
                'ttl': ttl_value,
                'timestamp': datetime.now().timestamp(),
                'last_accessed': datetime.now().timestamp(),
                'access_count': 0
            }
            
            try:
                # Write entry to file
                with open(file_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                # Add to registry
                key_hash = self._key_to_filename(key)
                self._registry[self.config.namespace].add(key_hash[:-6])
                self._update_stats(set_op=True)
                
            except (OSError, IOError, pickle.PickleError) as e:
                self._update_stats(error=True)
                raise FileCacheError(f"Error writing cache file: {str(e)}")
    
    async def _evict_items(self) -> int:
        """Evict items to maintain max cache size.
        
        Returns:
            Number of evicted items
        """
        ns = self.config.namespace
        ns_dir = os.path.join(self._cache_dir, ns)
        evicted = 0
        
        try:
            # Get all cache files with their last modified time
            files = []
            for filename in os.listdir(ns_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(ns_dir, filename)
                    mtime = os.path.getmtime(file_path)
                    files.append((file_path, mtime, filename))
            
            # Sort by last modified time (oldest first)
            files.sort(key=lambda x: x[1])
            
            # Remove oldest files to get below max_size
            to_remove = max(1, len(files) - self.config.max_size + 1)
            for i in range(to_remove):
                if i < len(files):
                    file_path, _, filename = files[i]
                    os.remove(file_path)
                    key_hash = self._filename_to_key(filename)
                    self._registry[ns].discard(key_hash)
                    evicted += 1
                    self._update_stats(eviction=True)
            
            return evicted
            
        except (OSError, IOError) as e:
            raise FileCacheError(f"Error evicting cache items: {str(e)}")
    
    async def invalidate(self, key: CacheKey) -> bool:
        """Invalidate a cache entry.
        
        Args:
            key: The cache key to invalidate
            
        Returns:
            True if the key was invalidated, False if it didn't exist
            
        Raises:
            CacheKeyError: If the key is invalid
            FileCacheError: If there's an error removing the cache file
        """
        if key is None:
            raise CacheKeyError("Cache key cannot be None")
        
        file_path = self._get_file_path(key)
        
        async with self._lock:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    key_hash = self._key_to_filename(key)
                    self._registry[self.config.namespace].discard(key_hash[:-6])
                    return True
                except (OSError, IOError) as e:
                    raise FileCacheError(f"Error removing cache file: {str(e)}")
            
            return False
    
    async def invalidate_namespace(self, namespace: Optional[str] = None) -> int:
        """Invalidate all cache entries in a namespace.
        
        Args:
            namespace: The namespace to invalidate (defaults to config.namespace)
            
        Returns:
            Number of invalidated cache entries
            
        Raises:
            FileCacheError: If there's an error removing cache files
        """
        ns = namespace or self.config.namespace
        ns_dir = os.path.join(self._cache_dir, ns)
        
        if not os.path.exists(ns_dir):
            return 0
        
        count = 0
        async with self._lock:
            try:
                for filename in os.listdir(ns_dir):
                    if filename.endswith('.cache'):
                        file_path = os.path.join(ns_dir, filename)
                        os.remove(file_path)
                        count += 1
                
                # Clear registry for this namespace
                self._registry[ns] = set()
                
                return count
                
            except (OSError, IOError) as e:
                raise FileCacheError(f"Error invalidating namespace: {str(e)}")
    
    async def clear(self) -> int:
        """Clear all cache entries in all namespaces.
        
        Returns:
            Number of cleared cache entries
            
        Raises:
            FileCacheError: If there's an error removing cache files
        """
        count = 0
        
        async with self._lock:
            try:
                # Count total files
                for ns in os.listdir(self._cache_dir):
                    ns_dir = os.path.join(self._cache_dir, ns)
                    if os.path.isdir(ns_dir):
                        for filename in os.listdir(ns_dir):
                            if filename.endswith('.cache'):
                                count += 1
                
                # Remove all files
                shutil.rmtree(self._cache_dir)
                
                # Recreate directory structure
                os.makedirs(self._cache_dir, exist_ok=True)
                self._ensure_namespace(self.config.namespace)
                
                # Clear registry
                self._registry.clear()
                self._registry[self.config.namespace] = set()
                
                return count
                
            except (OSError, IOError) as e:
                raise FileCacheError(f"Error clearing cache: {str(e)}")
    
    async def get_keys(self, pattern: Optional[str] = None) -> List[CacheKey]:
        """Get all cache keys matching a pattern in the current namespace.
        
        Args:
            pattern: Optional pattern to match keys against
            
        Returns:
            List of matching cache keys
            
        Raises:
            FileCacheError: If there's an error reading the cache directory
        """
        ns = self.config.namespace
        ns_dir = os.path.join(self._cache_dir, ns)
        
        if not os.path.exists(ns_dir):
            return []
        
        try:
            keys = []
            for filename in os.listdir(ns_dir):
                if filename.endswith('.cache'):
                    # For file cache, we can only return the hash as the key
                    key = self._filename_to_key(filename)
                    
                    if pattern is None or (isinstance(pattern, str) and fnmatch.fnmatch(key, pattern)):
                        keys.append(key)
            
            return keys
            
        except (OSError, IOError) as e:
            raise FileCacheError(f"Error reading cache directory: {str(e)}")
    
    async def get_size(self) -> int:
        """Get the current size of the default namespace cache.
        
        Returns:
            Number of items in the cache
            
        Raises:
            FileCacheError: If there's an error reading the cache directory
        """
        ns = self.config.namespace
        
        if ns in self._registry:
            return len(self._registry[ns])
        
        return 0
    
    async def has_key(self, key: CacheKey) -> bool:
        """Check if a key exists in the cache.
        
        Args:
            key: The cache key to check
            
        Returns:
            True if the key exists and has not expired, False otherwise
            
        Raises:
            FileCacheError: If there's an error reading the cache file
        """
        if key is None:
            return False
        
        file_path = self._get_file_path(key)
        
        if not os.path.exists(file_path):
            return False
        
        try:
            # Check if entry has expired
            with open(file_path, 'rb') as f:
                entry = pickle.load(f)
            
            now = datetime.now().timestamp()
            expiration_time = entry['timestamp'] + entry['ttl']
            
            if entry['ttl'] > 0 and now > expiration_time:
                # Remove expired entry
                os.remove(file_path)
                key_hash = self._key_to_filename(key)
                self._registry[self.config.namespace].discard(key_hash[:-6])
                return False
            
            return True
            
        except (OSError, IOError, pickle.PickleError) as e:
            raise FileCacheError(f"Error checking cache key: {str(e)}")
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries from the cache.
        
        Returns:
            Number of removed entries
            
        Raises:
            FileCacheError: If there's an error removing cache files
        """
        count = 0
        now = datetime.now().timestamp()
        
        async with self._lock:
            try:
                # Check each namespace
                for ns in os.listdir(self._cache_dir):
                    ns_dir = os.path.join(self._cache_dir, ns)
                    
                    if os.path.isdir(ns_dir):
                        # Check each file in namespace
                        for filename in os.listdir(ns_dir):
                            if filename.endswith('.cache'):
                                file_path = os.path.join(ns_dir, filename)
                                
                                # Check if entry has expired
                                try:
                                    with open(file_path, 'rb') as f:
                                        entry = pickle.load(f)
                                    
                                    expiration_time = entry['timestamp'] + entry['ttl']
                                    
                                    if entry['ttl'] > 0 and now > expiration_time:
                                        # Remove expired entry
                                        os.remove(file_path)
                                        
                                        # Update registry
                                        if ns in self._registry:
                                            key_hash = self._filename_to_key(filename)
                                            self._registry[ns].discard(key_hash)
                                        
                                        count += 1
                                except (pickle.PickleError, EOFError):
                                    # If file is corrupt, remove it
                                    os.remove(file_path)
                                    count += 1
                
                return count
                
            except (OSError, IOError) as e:
                raise FileCacheError(f"Error cleaning up expired entries: {str(e)}") 