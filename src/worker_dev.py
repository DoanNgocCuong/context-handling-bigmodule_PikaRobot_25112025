"""
Worker process with auto-reload for development.

This script watches for file changes and automatically restarts the worker.
Run: python src/worker_dev.py

For production, use: python src/worker.py
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# Add src/ to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ watchdog not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler


class WorkerReloadHandler(FileSystemEventHandler):
    """Handle file changes and restart worker."""
    
    def __init__(self, worker_script: str):
        self.worker_script = worker_script
        self.process = None
        self.restart_delay = 2  # Wait 2 seconds before restart
        self.last_restart = 0
        self.start_worker()
    
    def start_worker(self):
        """Start the worker process."""
        if self.process and self.process.poll() is None:
            print("🛑 Stopping existing worker process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        print("🚀 Starting worker process...")
        self.process = subprocess.Popen(
            [sys.executable, self.worker_script],
            stdout=sys.stdout,
            stderr=sys.stderr,
            cwd=os.path.dirname(self.worker_script)
        )
        self.last_restart = time.time()
    
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
        
        # Only watch Python files
        if not event.src_path.endswith('.py'):
            return
        
        # Ignore __pycache__ and .pyc files
        if '__pycache__' in event.src_path or event.src_path.endswith('.pyc'):
            return
        
        # Debounce: avoid multiple restarts in quick succession
        current_time = time.time()
        if current_time - self.last_restart < self.restart_delay:
            return
        
        print(f"\n🔄 File changed: {event.src_path}")
        print("⏳ Waiting for changes to settle...")
        time.sleep(self.restart_delay)
        print("🔄 Restarting worker...")
        self.start_worker()


def main():
    """Main entry point for development worker with auto-reload."""
    # Get paths
    script_dir = Path(__file__).parent
    worker_script = script_dir / "worker.py"
    app_dir = script_dir / "app"
    
    if not worker_script.exists():
        print(f"❌ Worker script not found: {worker_script}")
        sys.exit(1)
    
    print("=" * 60)
    print("🔧 Development Worker with Auto-Reload")
    print("=" * 60)
    print(f"📁 Watching: {app_dir}")
    print(f"📝 Worker script: {worker_script}")
    print("💡 Press CTRL+C to stop")
    print("=" * 60)
    print()
    
    # Create event handler
    event_handler = WorkerReloadHandler(str(worker_script))
    
    # Create observer
    observer = Observer()
    observer.schedule(event_handler, str(app_dir), recursive=True)
    observer.start()
    
    try:
        # Keep running
        while True:
            # Check if worker process is still alive
            if event_handler.process.poll() is not None:
                print("⚠️  Worker process died, restarting...")
                event_handler.start_worker()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping observer and worker...")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
            try:
                event_handler.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                event_handler.process.kill()
    finally:
        observer.join()
        print("✅ Stopped")


if __name__ == "__main__":
    main()

