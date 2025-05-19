import os
from typing import Dict, Any, List, Optional, Callable
from ..analyzers import analyze_python_ast
from ..utils import (
    read_file, 
    compute_file_hash, 
    FileProcessingQueue, 
    get_logger
)

logger = get_logger()

class FileProcessor:
    """Processor for analyzing Python files."""
    
    def __init__(self, 
                concurrency: int = 4,
                use_cache: bool = True,
                cache_dir: Optional[str] = None):
        """
        Initialize the file processor.
        
        Args:
            concurrency: Number of parallel workers
            use_cache: Whether to use caching
            cache_dir: Directory to store cache files
        """
        self.concurrency = concurrency
        self.use_cache = use_cache
        self.cache_dir = cache_dir
        
        if self.use_cache and not self.cache_dir:
            # Use a default cache directory
            self.cache_dir = os.path.expanduser("~/.python-code-graph/cache")
            os.makedirs(self.cache_dir, exist_ok=True)
            
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dict with file analysis results
        """
        content = read_file(file_path)
        line_count = len(content.splitlines())
        
        # Analyze the file
        analysis = analyze_python_ast(content)
        
        # Return the combined information
        return {
            'file_path': file_path,
            'line_count': line_count,
            **analysis
        }
        
    def process_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple Python files in parallel.
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            List of file analysis results
        """
        logger.info(f"Processing {len(file_paths)} files with {self.concurrency} workers")
        
        # Create processing queue
        queue = FileProcessingQueue(
            num_workers=self.concurrency,
            cache_dir=self.cache_dir,
            use_cache=self.use_cache
        )
        queue.start()
        
        # Add file processing tasks
        for file_path in file_paths:
            file_hash = None
            if self.use_cache:
                file_hash = compute_file_hash(file_path)
                
            queue.add_file_task(
                file_path=file_path,
                processor_func=self._process_file_task,
                file_hash=file_hash
            )
            
        # Wait for completion
        results = queue.wait_completion()
        queue.stop()
        
        logger.info(f"Completed processing {len(results)} files")
        return results
        
    def _process_file_task(self, file_path: str, content: str) -> Dict[str, Any]:
        """Process a file in a worker thread."""
        try:
            line_count = len(content.splitlines())
            
            # Analyze the file
            analysis = analyze_python_ast(content)
            
            # Return the combined information
            return {
                'file_path': file_path,
                'line_count': line_count,
                **analysis
            }
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return {
                'file_path': file_path,
                'error': str(e),
                'functions': [],
                'imports': [],
                'exports': [],
                'variables': []
            }