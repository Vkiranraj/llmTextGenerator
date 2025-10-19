#!/usr/bin/env python3
"""
Manual monitoring trigger for demo/testing purposes.
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent))

from scripts.monitor_urls import monitor_urls

if __name__ == "__main__":
    print("Manually triggering URL monitoring...")
    monitor_urls()
    print("Monitoring completed!")
