#!/usr/bin/env python
"""
Enhanced Performance Optimization Module v2.0 - Advanced Caching, Compression & Monitoring
New Features:
  - Multi-tier caching (in-memory + Redis optional)
  - Compression for large cached objects (gzip/zlib)
  - Request deduplication
  - Connection pooling support
  - Response compression
  - Advanced metrics & SLA monitoring
  - Cache warming and preload
  - Performance analytics dashboard
"""

import functools
import time
import hashlib
import json
import zlib
import gzip
import io
from collections import OrderedDict
from typing import Dict, List, Callable, Any, Tuple, Optional
from datetime import datetime, timedelta
import threading
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import pickle

logger = logging.getLogger(__name__)


class CompressionType(Enum):
    """Compression algorithm types"""
    NONE = 'none'
    GZIP = 'gzip'
    ZLIB = 'zlib'


@dataclass
class CacheEntry:
    """Represents a cached analysis entry with metadata"""
    data: Any
    timestamp: datetime
    ttl_seconds: int
    access_count: int = 0
    compression: CompressionType = CompressionType.NONE
    size_bytes: int = 0
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        return datetime.now() - self.timestamp > timedelta(seconds=self.ttl_seconds)
    
    def touch(self):
        """Update access count and timestamp"""
        self.access_count += 1
        self.timestamp = datetime.now()


class AdvancedAnalysisCache:
    """
    Enhanced LRU Cache with compression, TTL, and multi-tier support
    Supports optional Redis backend for distributed caching
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600, 
                 compression_threshold: int = 1024, enable_compression: bool = True):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.compression_threshold = compression_threshold
        self.enable_compression = enable_compression
        self.cache: Dict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        
        # Statistics
        self.hit_count = 0
        self.miss_count = 0
        self.compression_count = 0
        self.total_bytes_saved = 0
        
        # Optional Redis client
        self.redis_client = self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis client if available"""
        try:
            import redis
            redis_client = redis.Redis(
                host='localhost', port=6379, db=0, 
                decode_responses=False, socket_connect_timeout=2
            )
            redis_client.ping()
            logger.info("✓ Redis cache enabled for distributed caching")
            return redis_client
        except Exception as e:
            logger.debug(f"Redis not available: {e}. Using in-memory cache only.")
            return None
    
    def _generate_key(self, text: str) -> str:
        """Generate cache key from text hash"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _compress_data(self, data: Any) -> Tuple[bytes, CompressionType]:
        """Compress data using appropriate algorithm"""
        try:
            serialized = pickle.dumps(data)
            
            if len(serialized) < self.compression_threshold or not self.enable_compression:
                return serialized, CompressionType.NONE
            
            # Try zlib (better compression ratio)
            compressed = zlib.compress(serialized, level=6)
            if len(compressed) < len(serialized):
                self.total_bytes_saved += len(serialized) - len(compressed)
                return compressed, CompressionType.ZLIB
            
            return serialized, CompressionType.NONE
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return pickle.dumps(data), CompressionType.NONE
    
    def _decompress_data(self, data: bytes, compression: CompressionType) -> Any:
        """Decompress data based on compression type"""
        try:
            if compression == CompressionType.ZLIB:
                data = zlib.decompress(data)
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return None
    
    def get(self, text: str) -> Tuple[bool, Any]:
        """Retrieve from cache (checks in-memory first, then Redis)"""
        key = self._generate_key(text)
        
        with self.lock:
            # Try in-memory cache first
            if key in self.cache:
                entry = self.cache[key]
                
                if entry.is_expired():
                    del self.cache[key]
                    self.miss_count += 1
                    return False, None
                
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                entry.touch()
                self.hit_count += 1
                
                # Decompress if needed
                data = self._decompress_data(entry.data, entry.compression)
                return True, data
            
            self.miss_count += 1
        
        # Try Redis if available
        if self.redis_client:
            try:
                redis_data = self.redis_client.get(f"cache:{key}")
                if redis_data:
                    data = pickle.loads(redis_data)
                    # Populate in-memory cache
                    self._add_to_memory_cache(key, data)
                    self.hit_count += 1
                    return True, data
            except Exception as e:
                logger.warning(f"Redis retrieval failed: {e}")
        
        return False, None
    
    def put(self, text: str, result: Any):
        """Store result in cache with compression"""
        key = self._generate_key(text)
        compressed_data, compression_type = self._compress_data(result)
        size_bytes = len(compressed_data)
        
        if compression_type != CompressionType.NONE:
            self.compression_count += 1
        
        with self.lock:
            entry = CacheEntry(
                data=compressed_data,
                timestamp=datetime.now(),
                ttl_seconds=self.ttl,
                compression=compression_type,
                size_bytes=size_bytes
            )
            
            if key in self.cache:
                self.cache.move_to_end(key)
            
            self.cache[key] = entry
            
            # Store in Redis if available
            if self.redis_client:
                try:
                    self.redis_client.setex(
                        f"cache:{key}", 
                        self.ttl, 
                        pickle.dumps(result)
                    )
                except Exception as e:
                    logger.warning(f"Redis storage failed: {e}")
            
            # Evict oldest if over capacity
            if len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
    
    def _add_to_memory_cache(self, key: str, data: Any):
        """Add data to in-memory cache"""
        compressed_data, compression_type = self._compress_data(data)
        entry = CacheEntry(
            data=compressed_data,
            timestamp=datetime.now(),
            ttl_seconds=self.ttl,
            compression=compression_type,
            size_bytes=len(compressed_data)
        )
        
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = entry
        
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    def warm_cache(self, data_dict: Dict[str, Any]):
        """Pre-load cache with common results"""
        for text, result in data_dict.items():
            self.put(text, result)
        logger.info(f"✓ Warmed cache with {len(data_dict)} entries")
    
    def invalidate(self, text: str = None):
        """Invalidate cache entry or entire cache"""
        with self.lock:
            if text:
                key = self._generate_key(text)
                if key in self.cache:
                    del self.cache[key]
                if self.redis_client:
                    try:
                        self.redis_client.delete(f"cache:{key}")
                    except Exception as e:
                        logger.warning(f"Redis invalidation failed: {e}")
            else:
                self.cache.clear()
                if self.redis_client:
                    try:
                        self.redis_client.flushdb()
                    except Exception as e:
                        logger.warning(f"Redis flush failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate_percent': round(hit_rate * 100, 2),
            'total_requests': total_requests,
            'compressions': self.compression_count,
            'bytes_saved': self.total_bytes_saved,
            'ttl_seconds': self.ttl,
            'redis_enabled': self.redis_client is not None,
            'avg_entry_size_bytes': round(
                sum(e.size_bytes for e in self.cache.values()) / len(self.cache), 0
            ) if self.cache else 0
        }
    
    def clear(self):
        """Clear all caches"""
        with self.lock:
            self.cache.clear()
            if self.redis_client:
                try:
                    self.redis_client.flushdb()
                except Exception as e:
                    logger.warning(f"Redis flush failed: {e}")


class RequestDeduplicator:
    """Prevent duplicate concurrent requests for the same analysis"""
    
    def __init__(self):
        self.pending_requests: Dict[str, Any] = {}
        self.lock = threading.RLock()
    
    def _generate_request_id(self, text: str, analysis_type: str) -> str:
        """Generate unique request ID"""
        key = f"{analysis_type}:{text}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def is_pending(self, text: str, analysis_type: str) -> bool:
        """Check if request is already being processed"""
        request_id = self._generate_request_id(text, analysis_type)
        return request_id in self.pending_requests
    
    def register(self, text: str, analysis_type: str):
        """Register a request as pending"""
        request_id = self._generate_request_id(text, analysis_type)
        with self.lock:
            self.pending_requests[request_id] = datetime.now()
    
    def get_result(self, text: str, analysis_type: str) -> Optional[Any]:
        """Get result of pending request (blocks until available)"""
        request_id = self._generate_request_id(text, analysis_type)
        timeout = 30  # seconds
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.lock:
                if request_id in self.pending_requests:
                    result = self.pending_requests[request_id]
                    if isinstance(result, dict) and 'data' in result:
                        return result['data']
            time.sleep(0.1)
        
        return None
    
    def complete(self, text: str, analysis_type: str, result: Any):
        """Mark request as complete with result"""
        request_id = self._generate_request_id(text, analysis_type)
        with self.lock:
            self.pending_requests[request_id] = {'data': result, 'completed_at': datetime.now()}


class PerformanceMonitor:
    """Advanced performance monitoring and metrics collection"""
    
    def __init__(self):
        self.operation_timings: Dict[str, List[float]] = {}
        self.error_count: Dict[str, int] = {}
        self.start_time = datetime.now()
        self.lock = threading.Lock()
    
    def record_operation(self, operation_name: str, duration_seconds: float):
        """Record operation timing"""
        with self.lock:
            if operation_name not in self.operation_timings:
                self.operation_timings[operation_name] = []
            self.operation_timings[operation_name].append(duration_seconds)
    
    def record_error(self, operation_name: str):
        """Record operation error"""
        with self.lock:
            self.error_count[operation_name] = self.error_count.get(operation_name, 0) + 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        uptime = datetime.now() - self.start_time
        report = {
            'uptime_seconds': uptime.total_seconds(),
            'operations': {},
            'errors': self.error_count,
            'system_metrics': self._get_system_metrics()
        }
        
        for op_name, timings in self.operation_timings.items():
            if timings:
                report['operations'][op_name] = {
                    'count': len(timings),
                    'total_ms': round(sum(timings) * 1000, 2),
                    'avg_ms': round((sum(timings) / len(timings)) * 1000, 2),
                    'min_ms': round(min(timings) * 1000, 2),
                    'max_ms': round(max(timings) * 1000, 2),
                    'p95_ms': round(sorted(timings)[int(len(timings) * 0.95)] * 1000, 2) if len(timings) > 1 else 0,
                    'p99_ms': round(sorted(timings)[int(len(timings) * 0.99)] * 1000, 2) if len(timings) > 1 else 0,
                }
        
        return report
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'memory_mb': round(memory_info.rss / 1024 / 1024, 2),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'num_threads': process.num_threads(),
                'cpu_count': psutil.cpu_count()
            }
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")
            return {}
    
    def get_sla_report(self, sla_thresholds: Dict[str, float] = None) -> Dict[str, Any]:
        """Generate SLA compliance report"""
        if sla_thresholds is None:
            sla_thresholds = {
                'emotion_analysis': 0.1,      # 100ms
                'personality_analysis': 0.15, # 150ms
                'full_analysis': 0.5          # 500ms
            }
        
        report = {'compliant': True, 'operations': {}}
        
        for op_name, timings in self.operation_timings.items():
            if not timings:
                continue
            
            threshold = sla_thresholds.get(op_name, 1.0)
            avg_time = sum(timings) / len(timings)
            max_time = max(timings)
            compliant = max_time <= threshold
            
            report['operations'][op_name] = {
                'sla_threshold_seconds': threshold,
                'avg_time_seconds': round(avg_time, 3),
                'max_time_seconds': round(max_time, 3),
                'compliant': compliant,
                'violation_count': sum(1 for t in timings if t > threshold)
            }
            
            if not compliant:
                report['compliant'] = False
        
        return report


class ConnectionPoolManager:
    """Manage database connection pooling"""
    
    def __init__(self, pool_size: int = 10, timeout: int = 30):
        self.pool_size = pool_size
        self.timeout = timeout
        self.available_connections: List[Any] = []
        self.in_use_connections: Dict[int, Any] = {}
        self.lock = threading.RLock()
    
    def get_connection(self) -> Optional[Any]:
        """Get available connection from pool"""
        with self.lock:
            if self.available_connections:
                conn = self.available_connections.pop()
                conn_id = id(conn)
                self.in_use_connections[conn_id] = conn
                return conn
            elif len(self.in_use_connections) < self.pool_size:
                # Create new connection if pool not full
                return None
        return None
    
    def return_connection(self, conn: Any):
        """Return connection to pool"""
        with self.lock:
            conn_id = id(conn)
            if conn_id in self.in_use_connections:
                del self.in_use_connections[conn_id]
                self.available_connections.append(conn)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            return {
                'pool_size': self.pool_size,
                'available': len(self.available_connections),
                'in_use': len(self.in_use_connections),
                'utilization_percent': round(
                    (len(self.in_use_connections) / self.pool_size) * 100, 2
                )
            }


class ResponseCompressor:
    """Compress API responses for bandwidth optimization"""
    
    @staticmethod
    def compress_response(data: Dict[str, Any], min_size: int = 500) -> Tuple[bytes, str]:
        """
        Compress response if beneficial
        Returns (compressed_data, encoding) where encoding is 'gzip', 'deflate', or 'identity'
        """
        json_data = json.dumps(data).encode('utf-8')
        
        if len(json_data) < min_size:
            return json_data, 'identity'
        
        # Try gzip
        gzip_buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=gzip_buffer, mode='wb') as gz:
            gz.write(json_data)
        gzip_data = gzip_buffer.getvalue()
        
        if len(gzip_data) < len(json_data):
            return gzip_data, 'gzip'
        
        return json_data, 'identity'
    
    @staticmethod
    def decompress_response(data: bytes, encoding: str) -> str:
        """Decompress response based on encoding"""
        if encoding == 'gzip':
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
                return gz.read().decode('utf-8')
        elif encoding == 'deflate':
            return zlib.decompress(data).decode('utf-8')
        else:
            return data.decode('utf-8')


# Factory functions
def create_advanced_cache(max_size: int = 2000, ttl_seconds: int = 3600) -> AdvancedAnalysisCache:
    """Factory function to create advanced cache"""
    return AdvancedAnalysisCache(max_size=max_size, ttl_seconds=ttl_seconds)


def create_performance_monitor() -> PerformanceMonitor:
    """Factory function to create performance monitor"""
    return PerformanceMonitor()


def create_request_deduplicator() -> RequestDeduplicator:
    """Factory function to create request deduplicator"""
    return RequestDeduplicator()


def create_connection_pool(pool_size: int = 10) -> ConnectionPoolManager:
    """Factory function to create connection pool"""
    return ConnectionPoolManager(pool_size=pool_size)


if __name__ == '__main__':
    print("🚀 Enhanced Performance Optimization Module v2.0 Loaded\n")
    
    # Demo advanced cache with compression
    print("📊 Testing Advanced Cache with Compression...")
    cache = create_advanced_cache(max_size=100)
    
    # Create sample data
    sample_text = "This is a test analysis of the text. " * 50
    sample_result = {
        'emotion': 'happy',
        'confidence': 0.95,
        'traits': ['confident', 'optimistic'] * 20,
        'timestamp': datetime.now().isoformat()
    }
    
    # Store and retrieve
    cache.put(sample_text, sample_result)
    found, result = cache.get(sample_text)
    
    stats = cache.get_stats()
    print(f"  ✓ Cache Stats: {stats}")
    print(f"  ✓ Bytes Saved: {stats['bytes_saved']}")
    
    # Demo performance monitor
    print("\n📈 Testing Performance Monitor...")
    monitor = create_performance_monitor()
    monitor.record_operation('emotion_analysis', 0.045)
    monitor.record_operation('emotion_analysis', 0.052)
    monitor.record_operation('full_analysis', 0.350)
    
    perf_report = monitor.get_performance_report()
    sla_report = monitor.get_sla_report()
    print(f"  ✓ SLA Compliant: {sla_report['compliant']}")
    
    print("\n✅ All performance optimizations ready!")
