#!/usr/bin/env python3
"""
MongoDB Test Script for ResumeScan
This script tests all MongoDB functionality including connection, CRUD operations, and search.
"""

import os
import sys
import tempfile
from datetime import datetime
from io import BytesIO

# Add parent directory to Python path so we can import from db/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_connection():
    """Test MongoDB connection."""
    print("🔍 Testing MongoDB Connection...")
    try:
        from db.connection import db_connection
        collection = db_connection.get_collection()
        
        # Test basic connection
        result = collection.find_one()
        print("✅ MongoDB connection successful!")
        
        # Show database info
        db_name = db_connection.database.name
        collection_name = collection.name
        print(f"   Database: {db_name}")
        print(f"   Collection: {collection_name}")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_file_storage():
    """Test CV file storage functionality."""
    print("\n📁 Testing File Storage...")
    try:
        from db.cv_storage import cv_storage
        from db.models import CVFileMetadata
        
        # Create a mock uploaded file
        class MockUploadedFile:
            def __init__(self, name, content, content_type):
                self.name = name
                self.type = content_type
                self.size = len(content)
        
        # Test data
        test_content = b"This is a test PDF content for CV storage testing"
        mock_file = MockUploadedFile("test_resume.pdf", test_content, "application/pdf")
        
        # Test file storage
        file_id, metadata = cv_storage.store_cv_file(
            mock_file, 
            test_content, 
            job_description="Software Engineer"
        )
        
        print(f"✅ File stored successfully!")
        print(f"   File ID: {file_id}")
        print(f"   Filename: {metadata.filename}")
        print(f"   Size: {metadata.file_size} bytes")
        print(f"   Hash: {metadata.file_hash[:16]}...")
        
        return file_id, metadata
        
    except Exception as e:
        print(f"❌ File storage test failed: {e}")
        return None, None

def test_file_retrieval(file_id):
    """Test CV file retrieval."""
    print("\n📤 Testing File Retrieval...")
    try:
        from db.cv_storage import cv_storage
        
        if not file_id:
            print("⚠️ Skipping retrieval test (no file ID)")
            return False
        
        # Retrieve file
        file_content, metadata = cv_storage.get_cv_file(file_id)
        
        print(f"✅ File retrieved successfully!")
        print(f"   Content length: {len(file_content)} bytes")
        print(f"   Filename: {metadata.filename}")
        print(f"   Upload date: {metadata.upload_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ File retrieval test failed: {e}")
        return False

def test_analysis_update(file_id):
    """Test analysis results update."""
    print("\n🔍 Testing Analysis Update...")
    try:
        from db.cv_storage import cv_storage
        
        if not file_id:
            print("⚠️ Skipping analysis update test (no file ID)")
            return False
        
        # Mock analysis results
        analysis_results = {
            "score": 85,
            "missing_skills": ["Docker", "Kubernetes", "AWS"],
            "summary": "Strong candidate with good Python skills but missing DevOps experience",
            "questions": [
                "Tell me about your Python experience",
                "How would you approach learning Docker?",
                "Describe a challenging project you worked on"
            ]
        }
        
        # Update analysis results
        success = cv_storage.update_analysis_results(file_id, analysis_results)
        
        if success:
            print("✅ Analysis results updated successfully!")
            print(f"   Match Score: {analysis_results['score']}")
            print(f"   Missing Skills: {len(analysis_results['missing_skills'])} items")
            print(f"   Questions: {len(analysis_results['questions'])} generated")
        else:
            print("❌ Failed to update analysis results")
        
        return success
        
    except Exception as e:
        print(f"❌ Analysis update test failed: {e}")
        return False

def test_search_functionality():
    """Test CV search functionality."""
    print("\n🔍 Testing Search Functionality...")
    try:
        from db.cv_storage import cv_storage
        from db.models import CVSearchQuery
        
        # Test 1: Search all files
        print("   Test 1: Search all files")
        all_files = cv_storage.get_all_cv_files(limit=10)
        print(f"   ✅ Found {len(all_files)} total files")
        
        # Test 2: Search by filename
        print("   Test 2: Search by filename")
        search_query = CVSearchQuery(filename="test")
        results = cv_storage.search_cv_files(search_query)
        print(f"   ✅ Found {len(results)} files matching 'test'")
        
        # Test 3: Search by match score
        print("   Test 3: Search by match score")
        search_query = CVSearchQuery(min_match_score=80)
        results = cv_storage.search_cv_files(search_query)
        print(f"   ✅ Found {len(results)} files with score >= 80")
        
        # Test 4: Search with analysis results
        print("   Test 4: Search files with analysis")
        search_query = CVSearchQuery(has_analysis=True)
        results = cv_storage.search_cv_files(search_query)
        print(f"   ✅ Found {len(results)} analyzed files")
        
        return True
        
    except Exception as e:
        print(f"❌ Search functionality test failed: {e}")
        return False

def test_statistics():
    """Test database statistics."""
    print("\n📊 Testing Statistics...")
    try:
        from db.cv_storage import cv_storage
        
        stats = cv_storage.get_file_stats()
        
        print("✅ Statistics retrieved successfully!")
        print(f"   Total Files: {stats.get('total_files', 0)}")
        print(f"   Analyzed Files: {stats.get('analyzed_files', 0)}")
        print(f"   Unanalyzed Files: {stats.get('unanalyzed_files', 0)}")
        print(f"   Average Match Score: {stats.get('average_match_score', 0)}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Statistics test failed: {e}")
        return False

def cleanup_test_data():
    """Clean up test data."""
    print("\n🧹 Cleaning up test data...")
    try:
        from db.cv_storage import cv_storage
        from db.models import CVSearchQuery
        
        # Find test files
        search_query = CVSearchQuery(filename="test_resume")
        test_files = cv_storage.search_cv_files(search_query)
        
        deleted_count = 0
        for file_doc in test_files:
            file_id = file_doc.get('gridfs_file_id')
            if file_id and cv_storage.delete_cv_file(file_id):
                deleted_count += 1
        
        print(f"✅ Cleaned up {deleted_count} test files")
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False

def main():
    """Run all MongoDB tests."""
    print("🚀 ResumeScan MongoDB Test Suite")
    print("=" * 50)
    
    # Test results
    results = []
    
    # Test 1: Connection
    results.append(("Connection", test_connection()))
    
    if not results[0][1]:
        print("\n❌ Cannot proceed without database connection!")
        return False
    
    # Test 2: File Storage
    file_id, metadata = test_file_storage()
    results.append(("File Storage", file_id is not None))
    
    # Test 3: File Retrieval
    results.append(("File Retrieval", test_file_retrieval(file_id)))
    
    # Test 4: Analysis Update
    results.append(("Analysis Update", test_analysis_update(file_id)))
    
    # Test 5: Search Functionality
    results.append(("Search Functionality", test_search_functionality()))
    
    # Test 6: Statistics
    results.append(("Statistics", test_statistics()))
    
    # Test 7: Cleanup
    results.append(("Cleanup", cleanup_test_data()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MongoDB integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
