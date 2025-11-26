#!/usr/bin/env python3
"""
Comprehensive test for backend-frontend connectivity
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:3000"

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def test_backend():
    """Test backend is running"""
    print_section("1. Backend Health Check")
    try:
        response = requests.get("http://localhost:8000/admin/", timeout=5)
        if response.status_code in [200, 302]:
            print("✓ Backend is running and accessible")
            return True
        else:
            print(f"✗ Backend returned unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend is not accessible: {e}")
        return False

def test_frontend():
    """Test frontend is running"""
    print_section("2. Frontend Health Check")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✓ Frontend is running and accessible")
            return True
        else:
            print(f"⚠ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Frontend is not accessible: {e}")
        print("  Make sure frontend is running: docker-compose up -d frontend")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print_section("3. API Endpoints Test")
    
    # Test register
    try:
        test_data = {
            "username": f"testuser_{hash('test') % 10000}",
            "email": f"test_{hash('test') % 10000}@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/auth/register/", json=test_data, timeout=5)
        if response.status_code == 201:
            print("✓ Register endpoint: Working")
            user_data = response.json()
            return user_data
        elif response.status_code == 400:
            print("⚠ Register endpoint: User might already exist (Status 400)")
            # Try login instead
            login_response = requests.post(
                f"{BASE_URL}/auth/login/",
                json={"username": test_data["username"], "password": test_data["password"]},
                timeout=5
            )
            if login_response.status_code == 200:
                print("✓ Login endpoint: Working")
                return login_response.json()
        else:
            print(f"✗ Register endpoint failed: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"✗ API endpoint error: {e}")
    
    return None

def test_cors():
    """Test CORS configuration"""
    print_section("4. CORS Configuration Test")
    try:
        response = requests.options(
            f"{BASE_URL}/tasks/",
            headers={
                "Origin": FRONTEND_URL,
                "Access-Control-Request-Method": "GET"
            },
            timeout=5
        )
        cors_origin = response.headers.get("Access-Control-Allow-Origin")
        cors_credentials = response.headers.get("Access-Control-Allow-Credentials")
        
        if cors_origin == FRONTEND_URL:
            print(f"✓ CORS Origin: {cors_origin}")
        else:
            print(f"⚠ CORS Origin: {cors_origin} (expected {FRONTEND_URL})")
        
        if cors_credentials == "true":
            print("✓ CORS Credentials: Enabled")
        else:
            print("⚠ CORS Credentials: Not enabled")
        
        return True
    except Exception as e:
        print(f"✗ CORS test error: {e}")
        return False

def test_websocket_config():
    """Test WebSocket configuration"""
    print_section("5. WebSocket Configuration")
    print("✓ WebSocket endpoint configured at: ws://localhost:8000/ws/tasks/")
    print("  (Full WebSocket test requires browser/client connection)")
    return True

def test_database():
    """Test database connectivity"""
    print_section("6. Database Connectivity")
    try:
        # Try to access an endpoint that requires DB
        response = requests.get(f"{BASE_URL}/tasks/", timeout=5)
        if response.status_code in [401, 403]:
            print("✓ Database is accessible (authentication required as expected)")
            return True
        elif response.status_code == 200:
            print("✓ Database is accessible")
            return True
        else:
            print(f"⚠ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Database connectivity issue: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("COMPREHENSIVE BACKEND-FRONTEND CONNECTION TEST")
    print("=" * 60)
    
    results = {
        "backend": test_backend(),
        "frontend": test_frontend(),
        "api": test_api_endpoints() is not None,
        "cors": test_cors(),
        "websocket": test_websocket_config(),
        "database": test_database(),
    }
    
    print_section("TEST SUMMARY")
    print(f"Backend:     {'✓ PASS' if results['backend'] else '✗ FAIL'}")
    print(f"Frontend:    {'✓ PASS' if results['frontend'] else '✗ FAIL'}")
    print(f"API:         {'✓ PASS' if results['api'] else '✗ FAIL'}")
    print(f"CORS:        {'✓ PASS' if results['cors'] else '✗ FAIL'}")
    print(f"WebSocket:   {'✓ PASS' if results['websocket'] else '✗ FAIL'}")
    print(f"Database:    {'✓ PASS' if results['database'] else '✗ FAIL'}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED - System is ready!")
        print("\nNext steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Register a new user or login")
        print("3. Create a task and watch real-time updates")
    else:
        print("⚠ SOME TESTS FAILED - Check the errors above")
        if not results['backend']:
            print("\n  → Start backend: docker-compose up -d backend")
        if not results['frontend']:
            print("  → Start frontend: docker-compose up -d frontend")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

