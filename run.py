"""
Entrypoint for running the GST Verification Microservice.
"""

import sys
from app import create_app
from app.config import Config

app = create_app()

if __name__ == "__main__":
    print("=" * 65)
    print("  [*] GST Verification Microservice")
    print(f"  [+] Running at: http://{Config.HOST}:{Config.PORT}")
    print(f"  [+] Environment: {Config.ENVIRONMENT}")
    print(f"  [+] Session TTL: {Config.SESSION_TTL_SECONDS}s")
    print(f"  [+] Testbench UI: http://localhost:{Config.PORT}")
    print("=" * 65)

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=(Config.ENVIRONMENT == "development"),
        threaded=True
    )
