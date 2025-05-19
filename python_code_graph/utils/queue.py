import os
import queue
import threading
from typing import Callable, Any, List, Optional, Dict
import time

class TaskQueue:
    """
    A thread-safe task queue for batch processing files.
    
    This queue allows parallel processing of tasks with a controlled
    number of worker threads.
    """
    
    def __init__(self, num_workers: int = 4, max_queue_size: int = 1000):
        """
        Initialize the task queue.
        
        Args:
            num_workers: Number of parallel worker threads
            max_queue_size: Maximum number of tasks in the queue
        """
        self.task_queue = queue.Queue(maxsize=max_queue_size)
        self.result_queue = queue.Queue()
        self.num_workers = num_workers
        self.workers = []
        self.stop_event = threading.Event()
        self.results = []
        self.tasks_submitted = 0
        self.tasks_completed = 0
        
    def start(self):
        """Start the worker threads."""
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self._worker_loop)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
            
    def stop(self):
        """Stop all worker threads."""
        self.stop_event.set()
        for worker in self.workers:
            worker.join()
        self.workers = []
        
    def add_task(self, task_func: Callable, *args, **kwargs):
        """
        Add a task to the queue.
        
        Args:
            task_func: The function to execute
            *args, **kwargs: Arguments for the function
        """
        self.task_queue.put((task_func, args, kwargs))
        self.tasks_submitted += 1
        
    def _worker_loop(self):
        """Worker thread function."""
        while not self.stop_event.is_set():
            try:
                # Get a task from the queue with timeout
                task_func, args, kwargs = self.task_queue.get(timeout=0.1)
                
                # Execute the task
                try:
                    result = task_func(*args, **kwargs)
                    self.result_queue.put(('result', result))
                except Exception as e:
                    self.result_queue.put(('error', str(e)))
                    
                # Mark task as done
                self.task_queue.task_done()
                self.tasks_completed += 1
                
            except queue.Empty:
                # No task available, continue waiting
                continue
                
    def wait_completion(self) -> List[Any]:
        """
        Wait for all tasks to complete and return results.
        
        Returns:
            List of task results
        """
        # Wait for all tasks to be processed
        self.task_queue.join()
        
        # Get all results
        results = []
        errors = []
        
        while not self.result_queue.empty():
            result_type, data = self.result_queue.get()
            if result_type == 'result':
                results.append(data)
            else:
                errors.append(data)
                
        if errors:
            print(f"Completed with {len(errors)} errors")
            
        return results

class FileProcessingQueue(TaskQueue):
    """Specialized TaskQueue for processing files with caching."""
    
    def __init__(self, 
                num_workers: int = 4, 
                cache_dir: Optional[str] = None,
                use_cache: bool = True):
        """
        Initialize the file processing queue.
        
        Args:
            num_workers: Number of parallel worker threads
            cache_dir: Directory to store cache files
            use_cache: Whether to use caching
        """
        super().__init__(num_workers)
        self.cache_dir = cache_dir
        self.use_cache = use_cache
        self.cache = {}
        
        # Create cache directory if needed
        if self.use_cache and self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            
    def add_file_task(self, 
                     file_path: str, 
                     processor_func: Callable[[str, str], Any],
                     file_hash: Optional[str] = None):
        """
        Add a file processing task with caching support.
        
        Args:
            file_path: Path to the file
            processor_func: Function to process the file content
            file_hash: Optional file hash for cache lookup
        """
        if self.use_cache:
            # Compute file hash if not provided
            if file_hash is None:
                from .file_utils import compute_file_hash
                file_hash = compute_file_hash(file_path)
                
            # Check if result is in cache
            cache_key = f"{file_path}:{file_hash}"
            if cache_key in self.cache:
                self.result_queue.put(('result', self.cache[cache_key]))
                self.tasks_completed += 1
                return
                
            # Add task with caching
            self.add_task(self._process_with_cache, 
                         file_path, processor_func, cache_key)
        else:
            # Add task without caching
            self.add_task(self._process_file, file_path, processor_func)
            
    def _process_with_cache(self, 
                           file_path: str,
                           processor_func: Callable[[str, str], Any],
                           cache_key: str) -> Any:
        """Process a file and cache the result."""
        result = self._process_file(file_path, processor_func)
        self.cache[cache_key] = result
        return result
        
    def _process_file(self, 
                     file_path: str,
                     processor_func: Callable[[str, str], Any]) -> Any:
        """Process a file and return the result."""
        from .file_utils import read_file
        content = read_file(file_path)
        return processor_func(file_path, content)