import os
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """MongoDB connection manager for ResumeScan application."""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.cv_collection = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            # Get configuration from environment variables
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
            database_name = os.getenv('MONGODB_DATABASE', 'resumeScan')
            collection_name = os.getenv('MONGODB_COLLECTION', 'cv_files')
            
            # Create MongoDB client
            self.client = MongoClient(mongodb_uri)
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Get database and collection
            self.database = self.client[database_name]
            self.cv_collection = self.database[collection_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for better query performance."""
        try:
            # Create index on filename for faster searches
            self.cv_collection.create_index("filename")
            # Create index on upload_date for sorting
            self.cv_collection.create_index("upload_date")
            # Create index on file_hash for duplicate detection
            self.cv_collection.create_index("file_hash", unique=True)
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def get_collection(self) -> Collection:
        """Get the CV files collection."""
        return self.cv_collection
    
    def close_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global database connection instance
db_connection = MongoDBConnection()
