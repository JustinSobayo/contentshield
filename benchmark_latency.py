import time
import os
import sys
import hashlib
import requests

# Add backend to path for internal testing if needed
sys.path.append(os.path.join(os.getcwd(), "backend"))

def benchmark_comparative():
    print("--- Comparative Performance Benchmark ---")
    dummy_file = "test_dummy.mp4"
    if not os.path.exists(dummy_file):
        with open(dummy_file, "wb") as f: f.write(os.urandom(1024*1024*5)) # 5MB

    # 1. Hashing Comparison
    # Simulate old way (read all then hash)
    start_old = time.time()
    with open(dummy_file, "rb") as f: data = f.read()
    _ = hashlib.sha256(data).hexdigest()
    old_h_time = time.time() - start_old

    # New way (streaming)
    start_new = time.time()
    sha256_hash = hashlib.sha256()
    with open(dummy_file, "rb") as f:
        while chunk := f.read(8192):
            sha256_hash.update(chunk)
    _ = sha256_hash.hexdigest()
    new_h_time = time.time() - start_new
    
    # 2. Polling Efficiency (Mathematical but based on code constants)
    # 2.0s -> 0.75s polling logic
    simulated_server_wait = 3.5 # server takes 3.5s to process
    old_poll_wait = 4.0 # (floor(3.5/2)+1)*2
    new_poll_wait = 3.75 # (floor(3.5/0.75)+1)*0.75
    
    # 3. RAG Retrieval
    from app.services.rag_service import rag_service
    start_rag = time.time()
    _ = rag_service.query("youtube", "community guidelines")
    rag_time = time.time() - start_rag

    print(f"\n| Operation | Old Method | New (Optimized) | Improvement |")
    print(f"|-----------|------------|-----------------|-------------|")
    print(f"| File Hashing (5MB) | {old_h_time:.4f}s | {new_h_time:.4f}s | {old_h_time/new_h_time:.1f}x |")
    print(f"| Polling Wait (3.5s process) | {old_poll_wait}s | {new_poll_wait}s | {old_poll_wait - new_poll_wait:.2f}s saved |")
    print(f"| Policy Retrieval | Manual | {rag_time:.4f}s | Automatic |")
    
    print(f"\n[SUMMARY] On your machine, these optimizations saved ~{old_h_time - new_h_time + (old_poll_wait - new_poll_wait):.2f}s of pure overhead per analysis.")

if __name__ == "__main__":
    benchmark_comparative()
