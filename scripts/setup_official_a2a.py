import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major != 3 or version.minor < 10:
        print(f"❌ Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor} is compatible")
    return True

def uninstall_old_library():
    """Uninstall the old python-a2a library if present"""
    print("🧹 Cleaning up old python-a2a library...")
    run_command("pip uninstall python-a2a -y", "Uninstalling python-a2a")

def install_official_a2a():
    """Install the official Google A2A SDK"""
    print("📦 Installing official Google A2A SDK...")
    
    # Try uv first (recommended by Google)
    uv_result = run_command("uv --version", "Checking for uv")
    if uv_result:
        print("🚀 Using uv (recommended by Google)...")
        run_command("uv add a2a-sdk", "Installing a2a-sdk with uv")
    else:
        print("📦 Using pip...")
        run_command("pip install a2a-sdk", "Installing a2a-sdk with pip")

def install_dependencies():
    """Install other required dependencies"""
    print("📦 Installing other dependencies...")
    
    dependencies = [
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0", 
        "starlette>=0.27.0",
        "httpx>=0.25.0",
        "requests>=2.31.0",
        "websockets>=11.0",
        "pydantic>=2.0.0"
    ]
    
    for dep in dependencies:
        run_command(f"pip install '{dep}'", f"Installing {dep}")

def verify_installation():
    """Verify that the official A2A SDK is properly installed"""
    print("🔍 Verifying installation...")
    
    try:
        # Test import
        import subprocess
        result = subprocess.run([
            sys.executable, "-c", 
            "from a2a.server.apps import A2AStarletteApplication; print('✅ Official A2A SDK imported successfully')"
        ], capture_output=True, text=True, check=True)
        
        print(result.stdout.strip())
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Installation verification failed:")
        print(e.stderr)
        return False

def create_backup():
    """Create backup of old agent files"""
    print("💾 Creating backup of old agent files...")
    
    backup_dir = Path("backup_old_agents")
    backup_dir.mkdir(exist_ok=True)
    
    old_files = [
        "agents/data_processor.py",
        "agents/report_generator.py"
    ]
    
    for file_path in old_files:
        if Path(file_path).exists():
            backup_path = backup_dir / Path(file_path).name
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backed up {file_path} to {backup_path}")

def show_migration_summary():
    """Show summary of changes needed"""
    print("\n🎯 MIGRATION SUMMARY")
    print("=" * 60)
    print("✅ Official Google A2A SDK installed")
    print("✅ Dependencies updated")
    print("✅ Old python-a2a library removed")
    print()
    print("📋 NEXT STEPS:")
    print("1. Replace agent files with new official A2A versions")
    print("2. Update imports from 'python_a2a' to 'a2a'")
    print("3. Test the new implementation")
    print()
    print("🔧 KEY CHANGES:")
    print("- AgentExecutor replaces direct handle_task")
    print("- Message/EventQueue for responses")
    print("- Official AgentCard and AgentSkill types")
    print("- A2AStarletteApplication for server")
    print()
    print("🚀 READY FOR OFFICIAL GOOGLE A2A!")

def main():
    """Main setup function"""
    print("🐙 INKTRACE OFFICIAL GOOGLE A2A SETUP")
    print("=" * 50)
    print("Migrating from python-a2a to official Google A2A SDK")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    # Create backup
    create_backup()
    
    # Uninstall old library
    uninstall_old_library()
    
    # Install official SDK
    install_official_a2a()
    
    # Install other dependencies
    install_dependencies()
    
    # Verify installation
    if verify_installation():
        show_migration_summary()
        print("\n🎉 SETUP COMPLETE!")
    else:
        print("\n❌ SETUP FAILED!")
        print("Please check error messages above and try manual installation:")
        print("pip install a2a-sdk")
        sys.exit(1)

if __name__ == "__main__":
    main()
