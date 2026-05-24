"""
SMS Spam Detection API - Production Server Runner
==================================================
Runs the Flask API using Waitress (a production WSGI server).
Waitress is cross-platform and works reliably on Windows.

Usage:
    python run_server.py
    python run_server.py --host 0.0.0.0 --port 8080

Install dependency:
    pip install waitress
"""

import argparse
import sys

from waitress import serve
from app import app, load_model, logger


def main():
    parser = argparse.ArgumentParser(description='Run the SMS Spam Detection API')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Port to bind to (default: 5002)')
    parser.add_argument('--threads', type=int, default=4,
                        help='Number of worker threads (default: 4)')
    args = parser.parse_args()

    # Load model before starting server
    try:
        load_model()
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        sys.exit(1)

    logger.info(f"Starting production server at http://{args.host}:{args.port}")
    logger.info(f"Worker threads: {args.threads}")
    logger.info("Press Ctrl+C to stop the server")

    serve(app, host=args.host, port=args.port, threads=args.threads)


if __name__ == '__main__':
    main()
