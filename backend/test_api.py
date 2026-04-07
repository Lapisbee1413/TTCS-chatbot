"""
Test Backend API Endpoints
Run with: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_root():
    print("=" * 60)
    print("TEST 2: Root Endpoint")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_list_documents():
    print("=" * 60)
    print("TEST 3: List Documents")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/api/documents")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_upload():
    print("=" * 60)
    print("TEST 4: Upload Document")
    print("=" * 60)
    # You need to have a test file to upload
    print("Skipping upload test - requires actual file")
    print()

def test_query():
    print("=" * 60)
    print("TEST 5: Query Documents")
    print("=" * 60)
    payload = {
        "question": "Điều 2 quy định gì?",
        "model": "qwen2.5:1.5b",
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/api/query", json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")
    print()

def test_compare():
    print("=" * 60)
    print("TEST 6: Compare Versions")
    print("=" * 60)
    payload = {
        "article_name": "Điều 2",
        "source_v1": "HopDong_V1",
        "source_v2": "HopDong_V2",
        "model": "qwen2.5:1.5b"
    }
    response = requests.post(f"{BASE_URL}/api/compare", json=payload)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("\n🧪 TESTING BACKEND API\n")
    print("Make sure the server is running: uvicorn app.main:app --reload\n")
    
    try:
        test_health()
        test_root()
        test_list_documents()
        test_query()
        test_compare()
        
        print("✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")
