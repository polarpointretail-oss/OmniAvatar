#!/usr/bin/env python3
"""
Test script to verify OmniAvatar setup is working correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.abspath('.'))

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        # Test basic imports
        import torch
        print("✅ torch imported successfully")
        
        import transformers
        print("✅ transformers imported successfully")
        
        import librosa
        print("✅ librosa imported successfully")
        
        import peft
        print("✅ peft imported successfully")
        
        import xfuser
        print("✅ xfuser imported successfully")
        
        # Test OmniAvatar imports
        from OmniAvatar.utils.args_config import parse_args
        print("✅ OmniAvatar.utils.args_config imported successfully")
        
        from OmniAvatar.models.wav2vec import Wav2VecModel
        print("✅ OmniAvatar.models.wav2vec imported successfully")
        
        from OmniAvatar.models.model_manager import ModelManager
        print("✅ OmniAvatar.models.model_manager imported successfully")
        
        from OmniAvatar.wan_video import WanVideoPipeline
        print("✅ OmniAvatar.wan_video imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config_loading():
    """Test config file loading"""
    print("\nTesting config loading...")
    
    try:
        import yaml
        
        # Test loading the optimized config
        with open('configs/inference_1.3B_optimized.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        print("✅ Config file loaded successfully")
        print(f"   - Model path: {config.get('exp_path', 'NOT_FOUND')}")
        print(f"   - DIT path: {config.get('dit_path', 'NOT_FOUND')}")
        print(f"   - VAE path: {config.get('vae_path', 'NOT_FOUND')}")
        print(f"   - Text encoder path: {config.get('text_encoder_path', 'NOT_FOUND')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_file_existence():
    """Test that required files exist"""
    print("\nTesting file existence...")
    
    required_files = [
        'configs/inference_1.3B_optimized.yaml',
        'examples/infer_samples.txt',
        'examples/images/0000.jpeg',
        'examples/audios/0000.MP3',
        'scripts/inference.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_wav2vec_fix():
    """Test that the SDPA fix is in place"""
    print("\nTesting SDPA fix...")
    
    try:
        with open('OmniAvatar/models/wav2vec.py', 'r') as f:
            content = f.read()
        
        if 'self.config.output_attentions = False' in content:
            print("✅ SDPA fix found in forward method")
        else:
            print("❌ SDPA fix missing in forward method")
            return False
            
        if 'self.config.output_attentions = True' in content:
            print("✅ encode method has correct setting")
        else:
            print("❌ encode method missing correct setting")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ SDPA fix test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 OmniAvatar Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_loading,
        test_file_existence,
        test_wav2vec_fix
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! OmniAvatar should work correctly.")
        print("\nYou can now run:")
        print("torchrun --standalone --nproc_per_node=1 scripts/inference.py \\")
        print("  --config configs/inference_1.3B_optimized.yaml \\")
        print("  --input_file examples/infer_samples.txt")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main() 