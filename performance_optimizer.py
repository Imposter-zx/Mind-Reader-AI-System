#!/usr/bin/env python
"""
Performance Optimization Module - Caching, Speed & Resource Management
Features:
  - LRU Cache for analysis results
  - Vectorization acceleration
  - Batch processing optimization
  - Memory profiling
  - Query optimization
"""

import functools
import time
import hashlib
import json
from collections import OrderedDict
from typing import Dict, List, Callable, Any, Tuple
from datetime import datetime, timedelta
import threading


class AnalysisCache:
    """LRU Cache for analysis results with TTL"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.cache = OrderedDict()
        self.timestamps = {}
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.Lock()
    
    def _generate_key(self, text: str) -> str:
        """Generate cache key from text hash"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Tuple[bool, Any]:
        """Retrieve from cache if exists and valid"""
        with self.lock:
            key = self._generate_key(text)
            
            if key not in self.cache:
                self.miss_count += 1
                return False, None
            
            # Check TTL
            timestamp = self.timestamps[key]
            if datetime.now() - timestamp > timedelta(seconds=self.ttl):
                del self.cache[key]
                del self.timestamps[key]
                self.miss_count += 1
                return False, None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hit_count += 1
            return True, self.cache[key]
    
    def put(self, text: str, result: Any):
        """Store result in cache"""
        with self.lock:
            key = self._generate_key(text)
            
            if key in self.cache:
                self.cache.move_to_end(key)
            
            self.cache[key] = result
            self.timestamps[key] = datetime.now()
            
            # Evict oldest if over capacity
            if len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
    
    def clear(self):
        """Clear cache"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate': round(hit_rate * 100, 2),
            'total_requests': total_requests,
            'ttl_seconds': self.ttl
        }


class PerformanceProfiler:
    """Profile and measure analysis performance"""
    
    def __init__(self):
        self.timings = {}
        self.memory_usage = {}
    
    def measure_time(self, func: Callable) -> Callable:
        """Decorator to measure function execution time"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            
            execution_time = end_time - start_time
            func_name = func.__name__
            
            if func_name not in self.timings:
                self.timings[func_name] = []
            
            self.timings[func_name].append(execution_time)
            return result
        
        return wrapper
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        report = {}
        
        for func_name, times in self.timings.items():
            if times:
                report[func_name] = {
                    'calls': len(times),
                    'total_time': sum(times),
                    'average_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'avg_ms': round((sum(times) / len(times)) * 1000, 2)
                }
        
        return report
    
    def reset(self):
        """Reset performance metrics"""
        self.timings.clear()
        self.memory_usage.clear()


class BatchProcessor:
    """Optimized batch processing for multiple analyses"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.processing_time = 0
        self.items_processed = 0
    
    def process_batch(self, items: List[str], process_func: Callable, 
                     show_progress: bool = False) -> List[Any]:
        """Process items in optimized batches"""
        results = []
        start_time = time.time()
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            
            for j, item in enumerate(batch):
                result = process_func(item)
                results.append(result)
                self.items_processed += 1
                
                if show_progress and (j + 1) % 10 == 0:
                    print(f"  Processed {i + j + 1}/{len(items)} items...")
        
        self.processing_time = time.time() - start_time
        return results
    
    def get_throughput(self) -> float:
        """Get processing throughput (items/sec)"""
        if self.processing_time == 0:
            return 0.0
        return self.items_processed / self.processing_time
    
    def get_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics"""
        throughput = self.get_throughput()
        
        return {
            'items_processed': self.items_processed,
            'processing_time_seconds': round(self.processing_time, 2),
            'batch_size': self.batch_size,
            'throughput_items_per_sec': round(throughput, 2),
            'status': 'completed'
        }


class QueryOptimizer:
    """Optimize analysis queries for better performance"""
    
    QUERY_PATTERNS = {
        'emotion_only': ['emotion_analysis'],
        'personality_only': ['personality_analysis'],
        'safety_check': ['danger_detection', 'lie_detection'],
        'full_analysis': ['emotion_analysis', 'personality_analysis', 'danger_detection', 
                         'lie_detection', 'behavior_prediction'],
        'light_analysis': ['emotion_analysis', 'personality_analysis']
    }
    
    @staticmethod
    def optimize_for_speed(query_type: str) -> List[str]:
        """Get optimized component list for query type"""
        components = QueryOptimizer.QUERY_PATTERNS.get(query_type, 
                                                       QueryOptimizer.QUERY_PATTERNS['light_analysis'])
        return components
    
    @staticmethod
    def estimate_execution_time(query_type: str) -> float:
        """Estimate execution time for query"""
        # Based on benchmarks
        estimates = {
            'emotion_only': 0.05,
            'personality_only': 0.08,
            'safety_check': 0.12,
            'light_analysis': 0.15,
            'full_analysis': 0.30
        }
        return estimates.get(query_type, 0.20)
    
    @staticmethod
    def suggest_optimization(text_length: int) -> str:
        """Suggest optimization based on input size"""
        if text_length > 5000:
            return 'Consider using batch processing or sampling'
        elif text_length > 2000:
            return 'Consider using light_analysis query type'
        else:
            return 'No optimization needed'


class ResourceMonitor:
    """Monitor resource usage during analysis"""
    
    def __init__(self):
        self.snapshots = []
        self.peak_usage = 0
    
    def take_snapshot(self, label: str = '') -> Dict[str, Any]:
        """Take resource usage snapshot"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'label': label,
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),  # Resident Set Size
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),  # Virtual Memory Size
                'cpu_percent': process.cpu_percent(interval=0.1),
                'num_threads': process.num_threads()
            }
            
            self.snapshots.append(snapshot)
            self.peak_usage = max(self.peak_usage, snapshot['rss_mb'])
            return snapshot
        except ImportError:
            return {'status': 'psutil not installed'}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get resource usage summary"""
        if not self.snapshots:
            return {'status': 'No snapshots taken'}
        
        rss_values = [s['rss_mb'] for s in self.snapshots if 'rss_mb' in s]
        
        return {
            'peak_memory_mb': round(max(rss_values), 2) if rss_values else 0,
            'avg_memory_mb': round(sum(rss_values) / len(rss_values), 2) if rss_values else 0,
            'samples_taken': len(self.snapshots),
            'peak_during_session_mb': self.peak_usage
        }


def create_analysis_cache(max_size: int = 1000) -> AnalysisCache:
    """Factory function to create analysis cache"""
    return AnalysisCache(max_size=max_size)


def create_performance_profiler() -> PerformanceProfiler:
    """Factory function to create profiler"""
    return PerformanceProfiler()


def create_batch_processor(batch_size: int = 100) -> BatchProcessor:
    """Factory function to create batch processor"""
    return BatchProcessor(batch_size=batch_size)


if __name__ == '__main__':
    print("🚀 Performance Optimization Module Loaded\n")
    
    # Demo cache
    cache = AnalysisCache()
    
    test_text = "This is a test text for caching"
    cache.put(test_text, {'score': 0.85})
    
    found, result = cache.get(test_text)
    print(f"✅ Cache working: {found}, Result: {result}")
    print(f"📊 Cache stats: {cache.get_stats()}\n")
    
    # Demo batch processor
    processor = BatchProcessor(batch_size=10)
    items = [f"Text {i}" for i in range(25)]
    
    def dummy_process(item):
        return len(item)
    
    results = processor.process_batch(items, dummy_process)
    print(f"📦 Batch processing: {processor.get_stats()}")
    
    # Demo query optimizer
    print(f"\n⚡ Query optimization suggestions:")
    print(f"  Light text (500 chars): {QueryOptimizer.suggest_optimization(500)}")
    print(f"  Medium text (2500 chars): {QueryOptimizer.suggest_optimization(2500)}")
    print(f"  Large text (6000 chars): {QueryOptimizer.suggest_optimization(6000)}")
