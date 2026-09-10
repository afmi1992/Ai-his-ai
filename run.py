import subprocess
import sys
from pathlib import Path

def check_and_install_requirements():
    req_file = Path("requirements.txt")
    if req_file.exists():
        print("[iHIS Launcher] Checking and installing required dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    # 1. Automatically install/verify requirements
    try:
        check_and_install_requirements()
    except Exception as e:
        print(f"[iHIS Warning] Automated dependency verification skipped/failed: {e}")

    # 2. Import and run the Flask application
    print("[iHIS Launcher] Initializing application and seeding database context...")
    from app import create_app
    
    app = create_app()
    
    # 3. Automatically seed the drug database on startup
    with app.app_context():
        try:
            from seed_egypt_drugs import seed_database
            seed_database()
        except (ImportError, AttributeError):
            try:
                import seed_egypt_drugs
                if hasattr(seed_egypt_drugs, 'main'):
                    seed_egypt_drugs.main()
            except Exception as ex:
                print(f"[iHIS Warning] Automated drug seeding skipped/failed: {ex}")
    
    print("[iHIS Launcher] Starting development server at http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)

if __name__ == "__main__":
    main()