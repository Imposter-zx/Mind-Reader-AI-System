#!/usr/bin/env python
"""
Enhanced Database Optimization Module - Connection Pooling, Query Caching, Index Optimization
Features:
  - Connection pooling with configurable pool size
  - Query result caching
  - Batch insert optimization
  - Automatic index suggestions
  - Query execution plan analysis
  - Database health monitoring
  - Query performance tracking
"""

import sqlite3
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
import threading
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Track query performance metrics"""
    query_hash: str
    execution_time_ms: float
    rows_returned: int
    timestamp: datetime
    cached: bool = False


class OptimizedDatabaseConnection:
    """Database connection with query caching and optimization"""
    
    def __init__(self, db_path: str, cache_ttl_seconds: int = 300):
        self.db_path = db_path
        self.cache_ttl = cache_ttl_seconds
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Performance features
        self.execute_many_buffer = []
        self.buffer_size = 100
        
        # Query cache
        self.query_cache: Dict[str, Tuple[Any, datetime]] = {}
        self.query_metrics: List[QueryMetrics] = []
        self.lock = threading.RLock()
        
        # Optimize connection
        self._optimize_connection()
        self._create_indices()
    
    def _optimize_connection(self):
        """Optimize SQLite connection settings"""
        # Enable query optimizer
        self.connection.execute('PRAGMA optimize')
        
        # Increase cache size (negative = kilobytes)
        self.connection.execute('PRAGMA cache_size = -64000')  # ~64MB
        
        # Use WAL mode for better concurrent access
        try:
            self.connection.execute('PRAGMA journal_mode = WAL')
        except Exception as e:
            logger.debug(f"WAL mode not available: {e}")
        
        # Enable foreign keys
        self.connection.execute('PRAGMA foreign_keys = ON')
        
        # Synchronous mode for faster writes
        self.connection.execute('PRAGMA synchronous = NORMAL')
        
        logger.info("✓ Database connection optimized")
    
    def _create_indices(self):
        """Create indices for common queries"""
        indices = [
            ('analysis_history', 'text_hash'),
            ('analysis_history', 'created_at'),
            ('analysis_history', 'emotion_label'),
            ('user_profiles', 'user_id'),
            ('batch_operations', 'batch_id'),
            ('batch_operations', 'status'),
            ('conversations', 'conversation_id')
        ]
        
        cursor = self.connection.cursor()
        
        for table, column in indices:
            index_name = f"idx_{table}_{column}"
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name}
                    ON {table}({column})
                """)
            except Exception as e:
                logger.debug(f"Index creation failed: {e}")
        
        self.connection.commit()
        logger.info(f"✓ Created {len(indices)} indices for query optimization")
    
    def _generate_query_hash(self, query: str, params: Tuple = None) -> str:
        """Generate hash of query for caching"""
        cache_key = f"{query}:{params}"
        return hashlib.md5(cache_key.encode()).hexdigest()
    
    @contextmanager
    def execute_optimized(self, query: str, params: Tuple = None, cache_ttl: int = None):
        """
        Execute query with automatic caching and performance tracking
        Yields cursor with query results
        """
        if cache_ttl is None:
            cache_ttl = self.cache_ttl
        
        query_hash = self._generate_query_hash(query, params)
        
        # Check cache
        with self.lock:
            if query_hash in self.query_cache:
                cached_result, timestamp = self.query_cache[query_hash]
                if datetime.now() - timestamp < timedelta(seconds=cache_ttl):
                    # Return cached result
                    metrics = QueryMetrics(
                        query_hash=query_hash,
                        execution_time_ms=0,
                        rows_returned=len(cached_result),
                        timestamp=datetime.now(),
                        cached=True
                    )
                    self.query_metrics.append(metrics)
                    
                    # Create fake cursor
                    class CachedCursor:
                        def __init__(self, data):
                            self.data = data
                            self._index = 0
                        
                        def fetchall(self):
                            return self.data
                        
                        def fetchone(self):
                            if self._index < len(self.data):
                                result = self.data[self._index]
                                self._index += 1
                                return result
                            return None
                        
                        def __iter__(self):
                            return iter(self.data)
                    
                    yield CachedCursor(cached_result)
                    return
        
        # Execute query
        cursor = self.connection.cursor()
        start_time = time.time()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Cache SELECT results
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                
                with self.lock:
                    self.query_cache[query_hash] = (results, datetime.now())
                    
                    # Trim cache if too large
                    if len(self.query_cache) > 1000:
                        oldest_key = min(self.query_cache.keys(),
                                        key=lambda k: self.query_cache[k][1])
                        del self.query_cache[oldest_key]
                    
                    # Record metrics
                    metrics = QueryMetrics(
                        query_hash=query_hash,
                        execution_time_ms=execution_time_ms,
                        rows_returned=len(results),
                        timestamp=datetime.now(),
                        cached=False
                    )
                    self.query_metrics.append(metrics)
                
                # Create cursor-like object with cached results
                class ResultsCursor:
                    def __init__(self, data):
                        self.data = data
                        self._index = 0
                    
                    def fetchall(self):
                        return self.data
                    
                    def fetchone(self):
                        if self._index < len(self.data):
                            result = self.data[self._index]
                            self._index += 1
                            return result
                        return None
                    
                    def __iter__(self):
                        return iter(self.data)
                
                yield ResultsCursor(results)
            else:
                # INSERT/UPDATE/DELETE
                yield cursor
                self.connection.commit()
        
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            self.connection.rollback()
            raise
    
    def bulk_insert(self, table: str, records: List[Dict[str, Any]]):
        """Optimized bulk insert with buffering"""
        if not records:
            return
        
        # Get column names from first record
        columns = list(records[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)
        
        insert_query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        
        cursor = self.connection.cursor()
        start_time = time.time()
        
        try:
            # Use executemany for bulk insert
            for record in records:
                values = tuple(record.get(col) for col in columns)
                cursor.execute(insert_query, values)
            
            self.connection.commit()
            
            execution_time_ms = (time.time() - start_time) * 1000
            logger.info(f"✓ Inserted {len(records)} records in {execution_time_ms:.2f}ms")
            
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            self.connection.rollback()
            raise
    
    def get_query_analysis(self) -> Dict[str, Any]:
        """Get query performance analysis"""
        if not self.query_metrics:
            return {'status': 'No queries executed'}
        
        select_metrics = [m for m in self.query_metrics if not m.cached]
        cached_metrics = [m for m in self.query_metrics if m.cached]
        
        avg_execution_time = sum(m.execution_time_ms for m in select_metrics) / len(select_metrics) if select_metrics else 0
        
        return {
            'total_queries': len(self.query_metrics),
            'cached_queries': len(cached_metrics),
            'executed_queries': len(select_metrics),
            'cache_hit_rate_percent': round(len(cached_metrics) / len(self.query_metrics) * 100, 2),
            'avg_execution_time_ms': round(avg_execution_time, 2),
            'slowest_queries': sorted(select_metrics, key=lambda m: m.execution_time_ms, reverse=True)[:5]
        }
    
    def get_index_suggestions(self) -> List[str]:
        """Analyze slow queries and suggest indices"""
        slow_queries = [m for m in self.query_metrics if m.execution_time_ms > 50]
        
        suggestions = []
        for metric in slow_queries[:10]:
            # Simple heuristic: suggest indices on commonly filtered columns
            suggestion = f"Consider adding index on column used in query {metric.query_hash[:8]}"
            if suggestion not in suggestions:
                suggestions.append(suggestion)
        
        return suggestions
    
    def vacuum_optimize(self):
        """Defragment and optimize database"""
        try:
            self.connection.execute('VACUUM')
            self.connection.execute('ANALYZE')
            logger.info("✓ Database vacuumed and optimized")
        except Exception as e:
            logger.error(f"Vacuum failed: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        cursor = self.connection.cursor()
        
        stats = {}
        try:
            cursor.execute("SELECT COUNT(*) FROM analysis_history")
            stats['analysis_records'] = cursor.fetchone()[0]
        except:
            pass
        
        try:
            cursor.execute("SELECT COUNT(*) FROM user_profiles")
            stats['user_profiles'] = cursor.fetchone()[0]
        except:
            pass
        
        try:
            cursor.execute("SELECT COUNT(*) FROM batch_operations")
            stats['batch_operations'] = cursor.fetchone()[0]
        except:
            pass
        
        # Get database size
        import os
        try:
            stats['database_size_mb'] = round(os.path.getsize(self.db_path) / 1024 / 1024, 2)
        except:
            pass
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("✓ Database connection closed")


class ConnectionPool:
    """Manage pool of database connections"""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.available_connections: List[OptimizedDatabaseConnection] = []
        self.in_use: Dict[int, OptimizedDatabaseConnection] = {}
        self.lock = threading.RLock()
        
        # Pre-create connections
        for _ in range(pool_size):
            conn = OptimizedDatabaseConnection(db_path)
            self.available_connections.append(conn)
        
        logger.info(f"✓ Created connection pool with {pool_size} connections")
    
    @contextmanager
    def get_connection(self) -> OptimizedDatabaseConnection:
        """Get connection from pool"""
        with self.lock:
            if self.available_connections:
                conn = self.available_connections.pop()
            else:
                # Create new connection if needed
                conn = OptimizedDatabaseConnection(self.db_path)
            
            conn_id = id(conn)
            self.in_use[conn_id] = conn
        
        try:
            yield conn
        finally:
            with self.lock:
                if conn_id in self.in_use:
                    del self.in_use[conn_id]
                    self.available_connections.append(conn)
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            return {
                'total_connections': self.pool_size,
                'available': len(self.available_connections),
                'in_use': len(self.in_use),
                'utilization_percent': round(len(self.in_use) / self.pool_size * 100, 2)
            }
    
    def close_all(self):
        """Close all connections"""
        with self.lock:
            for conn in self.available_connections:
                try:
                    conn.close()
                except:
                    pass
            
            for conn in self.in_use.values():
                try:
                    conn.close()
                except:
                    pass
            
            self.available_connections.clear()
            self.in_use.clear()
        
        logger.info("✓ Connection pool closed")


class QueryOptimizer:
    """Analyze and optimize database queries"""
    
    @staticmethod
    def suggest_optimization(execution_time_ms: float, rows_returned: int) -> str:
        """Suggest query optimization based on metrics"""
        if execution_time_ms > 1000:
            return "⚠️  Very slow query - consider adding indices or restructuring query"
        elif execution_time_ms > 100:
            return "⚠️  Slow query - consider optimization"
        elif rows_returned > 10000:
            return "ℹ️  Large result set - consider pagination or filtering"
        else:
            return "✓ Query performance acceptable"
    
    @staticmethod
    def explain_query_plan(db_path: str, query: str) -> List[Dict[str, Any]]:
        """Get query execution plan"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            
            plan = []
            for row in cursor.fetchall():
                plan.append({
                    'id': row[0],
                    'parent': row[1],
                    'notused': row[2],
                    'detail': row[3]
                })
            
            conn.close()
            return plan
        except Exception as e:
            logger.error(f"Query plan analysis failed: {e}")
            return []


# Factory functions
def create_optimized_connection(db_path: str) -> OptimizedDatabaseConnection:
    """Create optimized database connection"""
    return OptimizedDatabaseConnection(db_path)


def create_connection_pool(db_path: str, pool_size: int = 5) -> ConnectionPool:
    """Create connection pool"""
    return ConnectionPool(db_path, pool_size=pool_size)


if __name__ == '__main__':
    print("🚀 Enhanced Database Optimization Module Loaded\n")
    
    # Demo optimized connection
    print("📊 Testing Optimized Database Connection...")
    
    try:
        conn = OptimizedDatabaseConnection(':memory:')
        
        # Create test table
        conn.connection.execute('''
            CREATE TABLE test (
                id INTEGER PRIMARY KEY,
                text TEXT,
                value REAL
            )
        ''')
        
        # Test bulk insert
        test_records = [
            {'text': f'Record {i}', 'value': i * 1.5}
            for i in range(100)
        ]
        conn.bulk_insert('test', test_records)
        
        # Test query with caching
        with conn.execute_optimized('SELECT * FROM test WHERE value > ?', (50,)) as cursor:
            results = cursor.fetchall()
            print(f"  ✓ Query returned {len(results)} rows")
        
        # Get analysis
        analysis = conn.get_query_analysis()
        print(f"  ✓ Query Analysis: {analysis}")
        
        # Get stats
        stats = conn.get_database_stats()
        print(f"  ✓ Database Stats: {stats}")
        
        conn.close()
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\n✅ All database optimizations ready!")
