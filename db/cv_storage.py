import io
from gridfs import GridFS
from typing import Optional, List, Dict, Any, Tuple
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
import logging

from .connection import db_connection
from .models import CVFileMetadata, CVSearchQuery

logger = logging.getLogger(__name__)

class CVStorageService:
    """Service for storing and retrieving CV files in MongoDB with GridFS."""
    
    def __init__(self):
        self.collection = db_connection.get_collection()
        self.fs = GridFS(db_connection.database)
    
    def store_cv_file(self, 
                     uploaded_file, 
                     file_content: bytes,
                     job_description: Optional[str] = None) -> Tuple[str, CVFileMetadata]:
        """
        Store CV file in GridFS and metadata in MongoDB.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            file_content: File content as bytes
            job_description: Associated job description
            
        Returns:
            Tuple of (file_id, metadata) where file_id is the GridFS file ID
            
        Raises:
            DuplicateKeyError: If file with same hash already exists
        """
        try:
            # Create metadata
            metadata = CVFileMetadata.create_from_upload(
                uploaded_file, file_content, job_description
            )
            
            # Store file in GridFS
            file_id = self.fs.put(
                file_content,
                filename=metadata.filename,
                content_type=metadata.content_type,
                metadata={
                    'file_hash': metadata.file_hash,
                    'upload_date': metadata.upload_date
                }
            )
            
            # Store metadata in collection with GridFS file reference
            metadata_dict = metadata.to_dict()
            metadata_dict['gridfs_file_id'] = file_id
            
            result = self.collection.insert_one(metadata_dict)
            metadata_dict['_id'] = result.inserted_id
            
            logger.info(f"Successfully stored CV file: {metadata.filename}")
            return str(file_id), metadata
            
        except DuplicateKeyError:
            logger.warning(f"Duplicate file detected: {metadata.filename}")
            raise
        except Exception as e:
            logger.error(f"Failed to store CV file: {e}")
            raise
    
    def get_cv_file(self, file_id: str) -> Tuple[bytes, CVFileMetadata]:
        """
        Retrieve CV file content and metadata.
        
        Args:
            file_id: GridFS file ID
            
        Returns:
            Tuple of (file_content, metadata)
        """
        try:
            # Get file from GridFS
            gridfs_file = self.fs.get(ObjectId(file_id))
            file_content = gridfs_file.read()
            
            # Get metadata from collection
            metadata_doc = self.collection.find_one({'gridfs_file_id': ObjectId(file_id)})
            if not metadata_doc:
                raise ValueError(f"Metadata not found for file ID: {file_id}")
            
            # Remove MongoDB-specific fields
            metadata_doc.pop('_id', None)
            metadata_doc.pop('gridfs_file_id', None)
            
            metadata = CVFileMetadata.from_dict(metadata_doc)
            
            return file_content, metadata
            
        except Exception as e:
            logger.error(f"Failed to retrieve CV file {file_id}: {e}")
            raise
    
    def update_analysis_results(self, 
                               file_id: str, 
                               analysis_results: Dict[str, Any]) -> bool:
        """
        Update CV file metadata with analysis results.
        
        Args:
            file_id: GridFS file ID
            analysis_results: Analysis results from resume processing
            
        Returns:
            True if update was successful
        """
        try:
            update_data = {
                'analysis_results': analysis_results,
                'match_score': analysis_results.get('score'),
                'missing_skills': analysis_results.get('missing_skills'),
                'profile_summary': analysis_results.get('summary'),
                'questions': analysis_results.get('questions')
            }
            
            result = self.collection.update_one(
                {'gridfs_file_id': ObjectId(file_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated analysis results for file: {file_id}")
                return True
            else:
                logger.warning(f"No document found to update for file: {file_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to update analysis results: {e}")
            return False
    
    def search_cv_files(self, 
                       search_query: CVSearchQuery,
                       limit: int = 50,
                       skip: int = 0) -> List[Dict[str, Any]]:
        """
        Search CV files based on criteria.
        
        Args:
            search_query: Search criteria
            limit: Maximum number of results
            skip: Number of results to skip (for pagination)
            
        Returns:
            List of CV file metadata documents
        """
        try:
            filter_dict = search_query.to_mongo_filter()
            
            cursor = self.collection.find(filter_dict).skip(skip).limit(limit)
            results = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for result in results:
                result['_id'] = str(result['_id'])
                result['gridfs_file_id'] = str(result['gridfs_file_id'])
            
            logger.info(f"Found {len(results)} CV files matching search criteria")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search CV files: {e}")
            return []
    
    def get_all_cv_files(self, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all CV files with pagination."""
        return self.search_cv_files(CVSearchQuery(), limit, skip)
    
    def delete_cv_file(self, file_id: str) -> bool:
        """
        Delete CV file and its metadata.
        
        Args:
            file_id: GridFS file ID
            
        Returns:
            True if deletion was successful
        """
        try:
            # Delete from GridFS
            self.fs.delete(ObjectId(file_id))
            
            # Delete metadata
            result = self.collection.delete_one({'gridfs_file_id': ObjectId(file_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Successfully deleted CV file: {file_id}")
                return True
            else:
                logger.warning(f"No metadata found to delete for file: {file_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete CV file {file_id}: {e}")
            return False
    
    def get_file_stats(self) -> Dict[str, Any]:
        """Get statistics about stored CV files."""
        try:
            total_files = self.collection.count_documents({})
            analyzed_files = self.collection.count_documents({'analysis_results': {'$ne': None}})
            
            # Get average match score
            pipeline = [
                {'$match': {'match_score': {'$ne': None}}},
                {'$group': {'_id': None, 'avg_score': {'$avg': '$match_score'}}}
            ]
            avg_score_result = list(self.collection.aggregate(pipeline))
            avg_score = avg_score_result[0]['avg_score'] if avg_score_result else 0
            
            return {
                'total_files': total_files,
                'analyzed_files': analyzed_files,
                'unanalyzed_files': total_files - analyzed_files,
                'average_match_score': round(avg_score, 2) if avg_score else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get file statistics: {e}")
            return {}

# Global storage service instance
cv_storage = CVStorageService()
