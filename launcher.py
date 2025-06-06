import sys
import os
import webbrowser
import threading
import time
import socket
import traceback

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"Warning: Could not detect local IP: {e}")
        return "localhost"

def open_browser():
    """Open browser after a short delay"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:5000')
        print("✓ Browser opened automatically")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print("Please manually open: http://localhost:5000")

def main():
    try:
        # Check if running in development mode
        dev_mode = '--dev' in sys.argv or os.getenv('SNAKE_DEV_MODE')
        
        # Set up the environment for PyInstaller
        if getattr(sys, 'frozen', False):
            # Running as executable
            bundle_dir = sys._MEIPASS
        else:
            # Running as script
            bundle_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Import app here to catch import errors
        try:
            from app import app, socketio
        except ImportError as e:
            print(f"ERROR: Could not import Flask app: {e}")
            print("Make sure all required files are present.")
            input("Press Enter to exit...")
            return
        
        # Get the local IP
        local_ip = get_local_ip()
        
        print("=" * 60)
        print("    MULTIPLAYER SNAKE BATTLE ARENA")
        if dev_mode:
            print("              (DEVELOPMENT MODE)")
        print("=" * 60)
        print(f"Local access: http://localhost:5000")
        print(f"Network access: http://{local_ip}:5000")
        print("=" * 60)
        print("Share the network URL with friends to play together!")
        if dev_mode:
            print("Development mode: Auto-reload enabled")
        print("Press Ctrl+C to stop the server")
        print("Opening browser automatically...")
        print("=" * 60)
        print()
        
        # Start browser in a separate thread (unless in dev mode with --no-browser)
        if '--no-browser' not in sys.argv:
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
        
        # Start the Flask-SocketIO server
        print("Starting server...")
        debug_mode = dev_mode and '--debug' in sys.argv
        socketio.run(app, host='0.0.0.0', port=5000, debug=debug_mode, allow_unsafe_werkzeug=True)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user. Thanks for playing!")
    except Exception as e:
        print(f"\nERROR starting server: {e}")
        print("\nFull error details:")
        traceback.print_exc()
        input("\nPress Enter to exit...")
    finally:
        print("\nServer shutdown complete.")

if __name__ == '__main__':
    main()