#!/usr/bin/env python
"""
Async Performance Module - Concurrent & Asynchronous Processing
Features:
  - Concurrent batch analysis
  - Task queue management
  - Async/await support
  - Background job processing
  - Result streaming
  - Progress tracking
"""

import asyncio
import concurrent.futures
import threading
import queue
import uuid
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import time
from functools import partial

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


@dataclass
class Task:
    """Represents a processing task"""
    task_id: str
    status: TaskStatus
    input_data: Any
    result: Any = None
    error: str = None
    progress: float = 0.0
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self):
        """Convert task to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['started_at'] = self.started_at.isoformat() if self.started_at else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data


class AsyncAnalysisProcessor:
    """Process analyses concurrently using thread/process pools"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.RLock()
    
    def submit_task(self, analysis_func: Callable, input_data: Any) -> str:
        """Submit task for async processing"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            status=TaskStatus.PENDING,
            input_data=input_data
        )
        
        with self.lock:
            self.tasks[task_id] = task
        
        # Submit to executor
        future = self.executor.submit(self._execute_task, task_id, analysis_func, input_data)
        future.add_done_callback(lambda f: self._handle_task_completion(task_id, f))
        
        logger.info(f"📝 Task {task_id} submitted for processing")
        return task_id
    
    def _execute_task(self, task_id: str, func: Callable, data: Any) -> Any:
        """Execute task and handle errors"""
        try:
            with self.lock:
                self.tasks[task_id].status = TaskStatus.RUNNING
                self.tasks[task_id].started_at = datetime.now()
            
            result = func(data)
            return result
        except Exception as e:
            logger.error(f"❌ Task {task_id} failed: {e}")
            with self.lock:
                self.tasks[task_id].error = str(e)
            raise
    
    def _handle_task_completion(self, task_id: str, future: concurrent.futures.Future):
        """Handle task completion"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return
            
            task.completed_at = datetime.now()
            
            try:
                result = future.result()
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.progress = 1.0
                logger.info(f"✅ Task {task_id} completed successfully")
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                logger.error(f"❌ Task {task_id} failed: {e}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status"""
        with self.lock:
            task = self.tasks.get(task_id)
            return task.to_dict() if task else None
    
    def get_task_result(self, task_id: str, timeout: float = 30.0) -> Any:
        """Get task result, blocking until complete or timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.lock:
                task = self.tasks.get(task_id)
                if not task:
                    raise ValueError(f"Task {task_id} not found")
                
                if task.status == TaskStatus.COMPLETED:
                    return task.result
                elif task.status == TaskStatus.FAILED:
                    raise RuntimeError(f"Task failed: {task.error}")
            
            time.sleep(0.1)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task or task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                return False
            
            task.status = TaskStatus.CANCELLED
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processor statistics"""
        with self.lock:
            total = len(self.tasks)
            completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
            failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
            running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
            pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
            
            return {
                'total_tasks': total,
                'completed': completed,
                'failed': failed,
                'running': running,
                'pending': pending,
                'max_workers': self.max_workers,
                'success_rate': round(completed / total * 100, 2) if total > 0 else 0
            }
    
    def shutdown(self, wait: bool = True):
        """Shutdown the executor"""
        self.executor.shutdown(wait=wait)


class BatchAnalyzer:
    """Analyze multiple texts in optimized batches"""
    
    def __init__(self, analysis_func: Callable, batch_size: int = 50, max_workers: int = 4):
        self.analysis_func = analysis_func
        self.batch_size = batch_size
        self.processor = AsyncAnalysisProcessor(max_workers=max_workers)
    
    def analyze_batch(self, texts: List[str], callback: Optional[Callable] = None) -> List[str]:
        """
        Analyze multiple texts and return task IDs
        Optional callback called for each completed task
        """
        task_ids = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            for text in batch:
                def analyze_wrapper(text_data):
                    result = self.analysis_func(text_data)
                    if callback:
                        callback(result)
                    return result
                
                task_id = self.processor.submit_task(analyze_wrapper, text)
                task_ids.append(task_id)
        
        return task_ids
    
    def get_all_results(self, task_ids: List[str], timeout: float = 300.0) -> List[Any]:
        """Get all results from batch"""
        results = []
        errors = []
        
        for task_id in task_ids:
            try:
                result = self.processor.get_task_result(task_id, timeout=timeout)
                results.append(result)
            except Exception as e:
                errors.append(f"Task {task_id}: {str(e)}")
        
        return {
            'results': results,
            'errors': errors,
            'total': len(task_ids),
            'successful': len(results),
            'failed': len(errors)
        }


class TaskQueue:
    """FIFO task queue for background processing"""
    
    def __init__(self, num_workers: int = 2):
        self.queue: queue.Queue = queue.Queue()
        self.num_workers = num_workers
        self.workers = []
        self.running = False
        self.results: Dict[str, Any] = {}
        self.lock = threading.Lock()
        self.start()
    
    def start(self):
        """Start worker threads"""
        self.running = True
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker, daemon=True, name=f"TaskWorker-{i}")
            worker.start()
            self.workers.append(worker)
        logger.info(f"✓ Started {self.num_workers} task workers")
    
    def _worker(self):
        """Worker thread main loop"""
        while self.running:
            try:
                task_id, func, args, kwargs = self.queue.get(timeout=1)
                
                try:
                    result = func(*args, **kwargs)
                    with self.lock:
                        self.results[task_id] = {'status': 'completed', 'result': result}
                    logger.debug(f"✓ Task {task_id} completed")
                except Exception as e:
                    with self.lock:
                        self.results[task_id] = {'status': 'failed', 'error': str(e)}
                    logger.error(f"✗ Task {task_id} failed: {e}")
                
                self.queue.task_done()
            except queue.Empty:
                continue
    
    def submit(self, func: Callable, *args, **kwargs) -> str:
        """Submit task to queue"""
        task_id = str(uuid.uuid4())
        self.queue.put((task_id, func, args, kwargs))
        return task_id
    
    def get_result(self, task_id: str, timeout: float = None) -> Any:
        """Get task result"""
        start_time = time.time()
        
        while True:
            with self.lock:
                if task_id in self.results:
                    result = self.results[task_id]
                    if result['status'] == 'completed':
                        return result['result']
                    else:
                        raise RuntimeError(f"Task failed: {result['error']}")
            
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {task_id} timed out")
            
            time.sleep(0.1)
    
    def stop(self):
        """Stop the queue"""
        self.running = False
        self.queue.join()
        for worker in self.workers:
            worker.join(timeout=5)
        logger.info("✓ Task queue stopped")


class ProgressTracker:
    """Track progress of long-running operations"""
    
    def __init__(self):
        self.progress_data: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def start_operation(self, operation_id: str, total_items: int):
        """Start tracking an operation"""
        with self.lock:
            self.progress_data[operation_id] = {
                'total': total_items,
                'completed': 0,
                'failed': 0,
                'start_time': datetime.now(),
                'end_time': None
            }
    
    def update_progress(self, operation_id: str, completed: int = 1, failed: int = 0):
        """Update progress"""
        with self.lock:
            if operation_id in self.progress_data:
                self.progress_data[operation_id]['completed'] += completed
                self.progress_data[operation_id]['failed'] += failed
    
    def complete_operation(self, operation_id: str):
        """Mark operation as complete"""
        with self.lock:
            if operation_id in self.progress_data:
                self.progress_data[operation_id]['end_time'] = datetime.now()
    
    def get_progress(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get operation progress"""
        with self.lock:
            if operation_id not in self.progress_data:
                return None
            
            data = self.progress_data[operation_id]
            total = data['total']
            completed = data['completed']
            percent = (completed / total * 100) if total > 0 else 0
            
            elapsed = (datetime.now() - data['start_time']).total_seconds()
            speed = completed / elapsed if elapsed > 0 else 0
            eta_seconds = (total - completed) / speed if speed > 0 else 0
            
            return {
                'total': total,
                'completed': completed,
                'failed': data['failed'],
                'percent_complete': round(percent, 2),
                'elapsed_seconds': round(elapsed, 2),
                'speed_items_per_sec': round(speed, 2),
                'eta_seconds': round(eta_seconds, 2)
            }


# Factory functions
def create_async_processor(max_workers: int = 4) -> AsyncAnalysisProcessor:
    """Create async processor"""
    return AsyncAnalysisProcessor(max_workers=max_workers)


def create_batch_analyzer(analysis_func: Callable, batch_size: int = 50) -> BatchAnalyzer:
    """Create batch analyzer"""
    return BatchAnalyzer(analysis_func, batch_size=batch_size)


def create_task_queue(num_workers: int = 2) -> TaskQueue:
    """Create task queue"""
    return TaskQueue(num_workers=num_workers)


def create_progress_tracker() -> ProgressTracker:
    """Create progress tracker"""
    return ProgressTracker()


if __name__ == '__main__':
    print("🚀 Async Performance Module Loaded\n")
    
    # Demo async processor
    print("🔄 Testing Async Processor...")
    
    def sample_analysis(text: str) -> Dict[str, Any]:
        """Sample analysis function"""
        time.sleep(0.1)  # Simulate processing
        return {'text': text, 'processed': True}
    
    processor = create_async_processor(max_workers=2)
    
    # Submit tasks
    task_ids = []
    for i in range(5):
        task_id = processor.submit_task(sample_analysis, f"Sample text {i}")
        task_ids.append(task_id)
    
    # Wait for completion
    time.sleep(0.3)
    stats = processor.get_stats()
    print(f"  ✓ Processor Stats: {stats}")
    
    print("\n✅ All async optimizations ready!")
