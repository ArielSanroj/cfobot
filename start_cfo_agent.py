#!/usr/bin/env python3
"""
Start the CFO Agent with Nanobot MCP integration.
This script starts the Nanobot MCP host with the CFO analysis capabilities.
"""

import os
import subprocess
import sys
from pathlib import Path

def main():
    """Start the CFO Agent."""
    # Set up environment variables
    os.environ["PYTHONPATH"] = str(Path(__file__).parent)
    
    # Check if Ollama is running
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print("❌ Error: Ollama is not running. Please start Ollama first:")
            print("   ollama serve")
            sys.exit(1)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Error: Ollama is not installed or not running.")
        print("   Please install Ollama: https://ollama.ai")
        print("   Then start it: ollama serve")
        sys.exit(1)
    
    # Check if the configured model is available
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if "llama3.1:latest" not in result.stdout:
            print("⚠️  Warning: llama3.1:latest model not found.")
            print("   Available models:")
            print(result.stdout)
            print("   To install: ollama pull llama3.1:latest")
            print("   Or update nanobot.yaml to use a different model")
    except Exception as e:
        print(f"⚠️  Warning: Could not check available models: {e}")
    
    # Start Nanobot with the CFO configuration
    config_file = Path(__file__).parent / "nanobot.yaml"
    
    if not config_file.exists():
        print(f"❌ Error: Configuration file not found: {config_file}")
        sys.exit(1)
    
    print("🚀 Starting CFO Financial Analyst Agent with Ollama...")
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
    print("Press Ctrl+C to stop the agent")
    print("-" * 50)
    
    try:
        # Run nanobot with the configuration
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