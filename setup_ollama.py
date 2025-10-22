#!/usr/bin/env python3
"""Setup script for Ollama integration with CFO Bot."""

import subprocess
import sys
import os
from pathlib import Path


def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_ollama():
    """Install Ollama."""
    print("Installing Ollama...")
    
    if sys.platform == "darwin":  # macOS
        subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], shell=True)
    elif sys.platform == "linux":
        subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], shell=True)
    else:
        print("Please install Ollama manually from https://ollama.ai/")
        return False
    
    return True


def pull_model(model_name="llama3.1:8b"):
    """Pull the specified Ollama model."""
    print(f"Pulling model {model_name}...")
    try:
        subprocess.run(['ollama', 'pull', model_name], check=True)
        print(f"Successfully pulled {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to pull model {model_name}: {e}")
        return False


def setup_environment():
    """Set up environment variables for Ollama."""
    env_file = Path(".env")
    
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write("# CFO Bot Environment Variables\n")
            f.write("CFOBOT_OLLAMA_ENABLED=true\n")
            f.write("CFOBOT_OLLAMA_MODEL=llama3.1:8b\n")
            f.write("CFOBOT_OLLAMA_BASE_URL=http://localhost:11434\n")
            f.write("CFOBOT_OLLAMA_TEMPERATURE=0.3\n")
            f.write("CFOBOT_OLLAMA_MAX_TOKENS=2000\n")
        print("Created .env file with Ollama configuration")
    else:
        print(".env file already exists")


def main():
    """Main setup function."""
    print("🤖 Setting up Ollama integration for CFO Bot...")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("Ollama not found. Installing...")
        if not install_ollama():
            print("Failed to install Ollama. Please install manually from https://ollama.ai/")
            return False
    else:
        print("✅ Ollama is already installed")
    
    # Pull the default model
    model_name = "llama3.1:8b"
    if not pull_model(model_name):
        print(f"Failed to pull model {model_name}")
        return False
    
    # Set up environment
    setup_environment()
    
    print("\n🎉 Ollama setup completed successfully!")
    print("\nNext steps:")
    print("1. Start Ollama service: ollama serve")
    print("2. Run CFO Bot with AI: python -m cfobot --verbose")
    print("3. Or disable AI: python -m cfobot --no-ai")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)