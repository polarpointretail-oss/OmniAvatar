#!/usr/bin/env python3
"""
Speed benchmark script for OmniAvatar inference optimization
Tests different configurations to find the fastest settings
"""

import subprocess
import time
import os
import json
from pathlib import Path
import tempfile

def create_test_input(duration_seconds=6):
    """Create a minimal test input for quick benchmarking"""
    content = f"A person speaking to camera for {duration_seconds} seconds@@examples/images/0000.jpeg@@examples/audios/0000.MP3"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        return f.name

def run_benchmark(config_file, test_input, description):
    """Run a single benchmark test"""
    print(f"\n🧪 Testing: {description}")
    print(f"   Config: {config_file}")
    
    cmd = [
        'torchrun', 
        '--standalone', 
        '--nproc_per_node=1',
        'scripts/profile_inference.py',
        '--config', config_file,
        '--input_file', test_input
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=1800)  # 30 min timeout
        elapsed = time.time() - start_time
        
        # Extract performance metrics from output
        lines = result.stdout.split('\n')
        metrics = {}
        
        for line in lines:
            if 'Total inference time:' in line:
                metrics['total_time'] = float(line.split(':')[1].strip().replace('s', ''))
            elif 'Generation speed:' in line:
                metrics['generation_speed'] = float(line.split(':')[1].strip().replace('x real-time', ''))
            elif 'Video duration:' in line:
                metrics['video_duration'] = float(line.split(':')[1].strip().replace('s', ''))
                
        print(f"✅ Success in {elapsed:.1f}s")
        if metrics:
            print(f"   Inference time: {metrics.get('total_time', 'N/A')}s")
            print(f"   Generation speed: {metrics.get('generation_speed', 'N/A')}x real-time")
            
        return {
            'config': config_file,
            'description': description,
            'success': True,
            'wall_time': elapsed,
            'metrics': metrics,
            'stdout': result.stdout[-1000:],  # Last 1000 chars for debugging
        }
        
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"⏰ Timeout after {elapsed:.1f}s")
        return {
            'config': config_file,
            'description': description,
            'success': False,
            'wall_time': elapsed,
            'error': 'timeout'
        }
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"❌ Failed after {elapsed:.1f}s")
        print(f"   Error: {e.stderr[-500:]}")  # Last 500 chars of error
        return {
            'config': config_file,
            'description': description,
            'success': False,
            'wall_time': elapsed,
            'error': e.stderr[-500:]
        }

def main():
    print("🚀 OmniAvatar Speed Benchmark")
    print("=" * 50)
    
    # Create test input
    test_input = create_test_input(6)  # 6 second test video
    print(f"📝 Created test input: {test_input}")
    
    # Define benchmark configurations
    benchmarks = [
        ('configs/inference.yaml', 'Original 14B (50 steps)'),
        ('configs/inference_optimized.yaml', 'Optimized 14B (20 steps + TeaCache)'),
        ('configs/inference_1.3B_optimized.yaml', 'Ultra-fast 1.3B (15 steps + TeaCache)'),
    ]
    
    # Check which configs exist
    available_benchmarks = []
    for config, desc in benchmarks:
        if os.path.exists(config):
            available_benchmarks.append((config, desc))
        else:
            print(f"⚠️  Skipping {desc} - config not found: {config}")
    
    if not available_benchmarks:
        print("❌ No valid configurations found!")
        return
    
    results = []
    
    print(f"\n🔍 Running {len(available_benchmarks)} benchmarks...")
    
    for config, description in available_benchmarks:
        result = run_benchmark(config, test_input, description)
        results.append(result)
        
        # Brief summary
        if result['success']:
            total_time = result.get('metrics', {}).get('total_time', result['wall_time'])
            speed = result.get('metrics', {}).get('generation_speed', 'N/A')
            print(f"   📊 {total_time:.1f}s ({speed}x real-time)")
        else:
            print(f"   ❌ Failed")
    
    # Final analysis
    print("\n" + "=" * 50)
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("=" * 50)
    
    successful_results = [r for r in results if r['success']]
    
    if successful_results:
        # Sort by total inference time
        successful_results.sort(key=lambda x: x.get('metrics', {}).get('total_time', x['wall_time']))
        
        print(f"\n🏆 RANKING (fastest to slowest):")
        for i, result in enumerate(successful_results, 1):
            total_time = result.get('metrics', {}).get('total_time', result['wall_time'])
            speed = result.get('metrics', {}).get('generation_speed', 'N/A')
            print(f"{i}. {result['description']}")
            print(f"   ⏱️  {total_time:.1f}s ({speed}x real-time)")
            
        # Speed comparison
        baseline = successful_results[-1]  # Slowest (usually original)
        fastest = successful_results[0]    # Fastest
        baseline_time = baseline.get('metrics', {}).get('total_time', baseline['wall_time'])
        fastest_time = fastest.get('metrics', {}).get('total_time', fastest['wall_time'])
        speedup = baseline_time / fastest_time
        
        print(f"\n🚀 SPEEDUP ANALYSIS:")
        print(f"   Baseline: {baseline['description']} ({baseline_time:.1f}s)")
        print(f"   Fastest:  {fastest['description']} ({fastest_time:.1f}s)")
        print(f"   Speedup:  {speedup:.1f}x faster")
        
        # Projections for longer videos
        print(f"\n📈 PROJECTIONS FOR LONGER VIDEOS:")
        for minutes in [1, 5, 10]:
            baseline_proj = baseline_time * (minutes * 60 / 6)  # Scale from 6s test
            fastest_proj = fastest_time * (minutes * 60 / 6)
            print(f"   {minutes} min video: {baseline_proj/60:.1f}min → {fastest_proj/60:.1f}min")
            
    else:
        print("❌ No successful benchmarks to compare")
    
    # Save detailed results
    results_file = f"benchmark_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Cleanup
    os.unlink(test_input)
    print(f"🧹 Cleaned up test input")
    
    print(f"\n✨ Benchmark complete!")

if __name__ == '__main__':
    main() 