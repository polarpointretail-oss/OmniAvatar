import subprocess
import os, sys
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse
from pathlib import Path

def run_inference_job(job_config):
    """Run a single inference job"""
    config_file, input_file, output_suffix, gpu_id = job_config
    
    env = os.environ.copy()
    env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
    
    cmd = [
        'torchrun', 
        '--standalone', 
        '--nproc_per_node=1',
        'scripts/inference.py',
        '--config', config_file,
        '--input_file', input_file
    ]
    
    print(f"🚀 Starting job on GPU {gpu_id}: {config_file} -> {input_file}")
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=True)
        elapsed = time.time() - start_time
        print(f"✅ GPU {gpu_id} completed in {elapsed:.1f}s: {input_file}")
        return {'gpu': gpu_id, 'success': True, 'time': elapsed, 'file': input_file}
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"❌ GPU {gpu_id} failed after {elapsed:.1f}s: {input_file}")
        print(f"Error: {e.stderr}")
        return {'gpu': gpu_id, 'success': False, 'time': elapsed, 'file': input_file, 'error': e.stderr}

def split_input_file(input_file, num_chunks):
    """Split input file into chunks for parallel processing"""
    with open(input_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    chunk_size = max(1, len(lines) // num_chunks)
    chunks = []
    
    for i in range(0, len(lines), chunk_size):
        chunk_lines = lines[i:i + chunk_size]
        chunk_file = f"{input_file}_chunk_{i//chunk_size}.txt"
        with open(chunk_file, 'w') as f:
            f.write('\n'.join(chunk_lines))
        chunks.append(chunk_file)
    
    return chunks

def main():
    parser = argparse.ArgumentParser(description='Run OmniAvatar inference in parallel across multiple GPUs')
    parser.add_argument('--config', required=True, help='Base config file to use')
    parser.add_argument('--input_file', required=True, help='Input file with prompts')
    parser.add_argument('--gpus', default='0,1,2,3', help='Comma-separated list of GPU IDs to use')
    parser.add_argument('--per_gpu_jobs', type=int, default=1, help='Number of parallel jobs per GPU')
    parser.add_argument('--split_input', action='store_true', help='Split input file across GPUs')
    
    args = parser.parse_args()
    
    gpu_ids = [int(x.strip()) for x in args.gpus.split(',')]
    total_processes = len(gpu_ids) * args.per_gpu_jobs
    
    print(f"🔧 Parallel Inference Setup:")
    print(f"   GPUs: {gpu_ids}")
    print(f"   Jobs per GPU: {args.per_gpu_jobs}")
    print(f"   Total parallel jobs: {total_processes}")
    print(f"   Config: {args.config}")
    print(f"   Input: {args.input_file}")
    
    # Prepare job configurations
    jobs = []
    
    if args.split_input:
        # Split input file and assign chunks to different processes
        chunk_files = split_input_file(args.input_file, total_processes)
        for i, chunk_file in enumerate(chunk_files):
            gpu_id = gpu_ids[i % len(gpu_ids)]
            jobs.append((args.config, chunk_file, f"chunk_{i}", gpu_id))
    else:
        # Run the same input file on all processes (useful for different configs)
        for gpu_id in gpu_ids:
            for job_idx in range(args.per_gpu_jobs):
                jobs.append((args.config, args.input_file, f"gpu{gpu_id}_job{job_idx}", gpu_id))
    
    print(f"📋 Prepared {len(jobs)} jobs")
    
    # Run jobs in parallel
    start_time = time.time()
    results = []
    
    with ProcessPoolExecutor(max_workers=total_processes) as executor:
        future_to_job = {executor.submit(run_inference_job, job): job for job in jobs}
        
        for future in as_completed(future_to_job):
            result = future.result()
            results.append(result)
            
            successful = sum(1 for r in results if r['success'])
            failed = sum(1 for r in results if not r['success'])
            print(f"📊 Progress: {len(results)}/{len(jobs)} ({successful} ✅, {failed} ❌)")
    
    total_time = time.time() - start_time
    successful_jobs = [r for r in results if r['success']]
    failed_jobs = [r for r in results if not r['success']]
    
    print(f"\n🎯 PARALLEL EXECUTION SUMMARY:")
    print(f"   Total time: {total_time:.1f}s")
    print(f"   Successful jobs: {len(successful_jobs)}/{len(jobs)}")
    print(f"   Failed jobs: {len(failed_jobs)}")
    
    if successful_jobs:
        avg_time = sum(r['time'] for r in successful_jobs) / len(successful_jobs)
        min_time = min(r['time'] for r in successful_jobs)
        max_time = max(r['time'] for r in successful_jobs)
        print(f"   Job times: avg={avg_time:.1f}s, min={min_time:.1f}s, max={max_time:.1f}s")
        print(f"   Speedup vs sequential: {sum(r['time'] for r in successful_jobs) / total_time:.1f}x")
    
    if failed_jobs:
        print(f"\n❌ Failed jobs:")
        for job in failed_jobs:
            print(f"   GPU {job['gpu']}: {job['file']}")
    
    # Cleanup chunk files if created
    if args.split_input:
        for chunk_file in chunk_files:
            if os.path.exists(chunk_file):
                os.remove(chunk_file)
                print(f"🧹 Cleaned up {chunk_file}")

if __name__ == '__main__':
    main()