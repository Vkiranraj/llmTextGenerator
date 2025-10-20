#!/usr/bin/env python3
"""
Test script for API rate limiting.
This script tests that rate limits are properly enforced on API endpoints.
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_rate_limiting():
    """Test rate limiting on different endpoints."""
    
    print("🧪 Testing API Rate Limiting")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print()
    
    # Test 1: Job Creation Rate Limit (10/minute)
    print("Test 1: Job Creation Rate Limit (10/minute)")
    print("-" * 60)
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(12):  # Try 12 requests (should hit limit at 11)
        try:
            response = requests.post(
                f"{BASE_URL}/jobs/",
                json={"url": f"https://example{i}.com"},
                timeout=5
            )
            
            if response.status_code == 200 or response.status_code == 400:
                # 200 = success, 400 = validation error (both count as non-rate-limited)
                success_count += 1
                print(f"  Request {i+1}: ✅ Status {response.status_code}")
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"  Request {i+1}: 🛑 Rate Limited (429)")
                print(f"    Response: {response.text}")
            else:
                print(f"  Request {i+1}: ⚠️  Unexpected status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Error: Cannot connect to {BASE_URL}")
            print(f"  Make sure the server is running!")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print()
    print(f"Results: {success_count} successful, {rate_limited_count} rate limited")
    
    if rate_limited_count >= 2:  # Should hit limit at least twice (requests 11 and 12)
        print("✅ Rate limiting is working correctly!")
    else:
        print("⚠️  Rate limiting may not be working as expected")
    
    print()
    
    # Test 2: Progress Endpoint Rate Limit (180/minute = 3/second)
    print("Test 2: Progress Endpoint Rate Limit (3/second)")
    print("-" * 60)
    
    # Make rapid requests (more than 3 per second)
    progress_success = 0
    progress_limited = 0
    
    for i in range(10):  # 10 rapid requests
        try:
            response = requests.get(
                f"{BASE_URL}/jobs/1/progress",
                timeout=5
            )
            
            if response.status_code == 404:
                # Job doesn't exist, but we're testing rate limiting
                progress_success += 1
                print(f"  Request {i+1}: ✅ Not rate limited")
            elif response.status_code == 429:
                progress_limited += 1
                print(f"  Request {i+1}: 🛑 Rate Limited")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(0.1)  # Very short delay to simulate rapid polling
    
    print()
    print(f"Results: {progress_success} successful, {progress_limited} rate limited")
    print()
    
    # Test 3: Monitor Trigger Rate Limit (5/hour)
    print("Test 3: Monitor Trigger Rate Limit (5/hour)")
    print("-" * 60)
    print("Making 6 requests to /monitor/trigger...")
    
    monitor_success = 0
    monitor_limited = 0
    
    for i in range(6):
        try:
            response = requests.post(
                f"{BASE_URL}/monitor/trigger",
                timeout=10
            )
            
            if response.status_code in [200, 500]:
                # 200 = success, 500 = internal error (not rate limit)
                monitor_success += 1
                print(f"  Request {i+1}: ✅ Status {response.status_code}")
            elif response.status_code == 429:
                monitor_limited += 1
                print(f"  Request {i+1}: 🛑 Rate Limited (429)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print()
    print(f"Results: {monitor_success} successful, {monitor_limited} rate limited")
    
    if monitor_limited >= 1:  # Should hit limit on 6th request
        print("✅ Monitor trigger rate limiting is working!")
    else:
        print("⚠️  Monitor trigger rate limiting may not be working")
    
    print()
    print("=" * 60)
    print("Rate Limiting Test Complete!")
    print()
    
    return True

if __name__ == "__main__":
    print()
    print("⚠️  WARNING: This test will make many requests to your API.")
    print("   Make sure your server is running at http://localhost:8000")
    print()
    
    try:
        # Quick connectivity check
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is reachable")
            print()
            test_rate_limiting()
        else:
            print(f"⚠️  Server returned unexpected status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   Please start your server with: uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
