#!/usr/bin/env python3
"""
Start the CFO Agent with Ollama (local AI) integration.
This script starts the Nanobot MCP host with the CFO analysis capabilities using local Ollama models.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_ollama_running():
    """Check if Ollama is running and return available models."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "Ollama not found or not responding"

def ensure_model_available(model_name="llama3.1:latest"):
    """Ensure the required model is available, offer to install if not."""
    running, output = check_ollama_running()
    
    if not running:
        print("❌ Error: Ollama is not running.")
        print("   Please start Ollama first:")
        print("   ollama serve")
        return False
    
    if model_name not in output:
        print(f"⚠️  Model '{model_name}' not found.")
        print("   Available models:")
        print(output)
        print(f"\n   To install the model, run:")
        print(f"   ollama pull {model_name}")
        
        response = input(f"\n   Would you like me to install {model_name} now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            print(f"   Installing {model_name}...")
            try:
                result = subprocess.run(["ollama", "pull", model_name], check=True)
                print(f"   ✅ {model_name} installed successfully!")
                return True
            except subprocess.CalledProcessError as e:
                print(f"   ❌ Failed to install {model_name}: {e}")
                return False
        else:
            print("   Please install the model manually and try again.")
            return False
    
    return True

def main():
    """Start the CFO Agent with Ollama."""
    # Set up environment variables
    os.environ["PYTHONPATH"] = str(Path(__file__).parent)
    
    print("🤖 CFO Agent with Ollama (Local AI)")
    print("=" * 50)
    
    # Check Ollama and model availability
    if not ensure_model_available("llama3.1:latest"):
        sys.exit(1)
    
    # Start Nanobot with the Ollama configuration
    config_file = Path(__file__).parent / "nanobot_ollama.yaml"
    
    if not config_file.exists():
        print(f"❌ Error: Configuration file not found: {config_file}")
        sys.exit(1)
    
    print("\n🚀 Starting CFO Financial Analyst Agent...")
    print(f"📁 Configuration: {config_file}")
    print("🤖 Using model: llama3.1:latest (local Ollama)")
    print("🌐 Web UI will be available at: http://localhost:8080")
    print("💬 You can chat with the CFO agent through the web interface")
    print()
    print("Available capabilities:")
    print("  • Analyze financial reports automatically")
    print("  • Generate KPI summaries")
    print("  • Provide budget execution analysis")
    print("  • Create consolidated balance summaries")
    print("  • Upload and process new Excel reports")
    print("  • List available financial reports")
    print()
    print("💡 Note: All processing happens locally with Ollama - no API keys needed!")
    print("🔒 Your data stays on your machine - completely private!")
    print("Press Ctrl+C to stop the agent")
    print("-" * 50)
    
    try:
        # Run nanobot with the Ollama configuration
        subprocess.run([
            "nanobot", "run", str(config_file)
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Nanobot: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 CFO Agent stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()