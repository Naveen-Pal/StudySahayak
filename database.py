from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from config import Config
import logging

class Database:
    """Database operations for MongoDB"""
    
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB_NAME]
        self.collection = self.db[Config.MONGO_COLLECTION_NAME]
        self.users_collection = self.db['users']
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Index for users collection
            self.users_collection.create_index('username', unique=True)
            
            # Indexes for content collection
            self.collection.create_index([('user_id', 1), ('created_at', -1)])
            self.collection.create_index('content_id')
            
        except Exception as e:
            logging.warning(f"Could not create indexes: {e}")
    
    def create_user(self, username, password_hash):
        """Create a new user"""
        user_data = {
            'username': username,
            'password': password_hash,
            'created_at': datetime.utcnow()
        }
        
        result = self.users_collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user(self, username):
        """Get user by username"""
        return self.users_collection.find_one({'username': username})
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.users_collection.find_one({'_id': ObjectId(user_id)})
    
    def store_content(self, user_id, title, content, content_type, metadata=None):
        """Store processed content in database"""
        content_data = {
            'user_id': user_id,
            'title': title,
            'content': content,
            'content_type': content_type,
            'metadata': metadata or {},
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.collection.insert_one(content_data)
        return str(result.inserted_id)
    
    def get_content(self, content_id, user_id):
        """Get specific content by ID and user ID"""
        try:
            return self.collection.find_one({
                '_id': ObjectId(content_id),
                'user_id': user_id
            })
        except:
            return None
    
    def get_user_contents(self, user_id):
        """Get all contents for a specific user"""
        contents = list(self.collection.find(
            {'user_id': user_id},
            {'content': 0}  # Exclude full content for listing
        ).sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for content in contents:
            content['_id'] = str(content['_id'])
            # Keep datetime objects for template formatting
            # Only convert to string for API responses if needed
        
        return contents
    
    def update_content(self, content_id, user_id, updates):
        """Update content"""
        updates['updated_at'] = datetime.utcnow()
        
        result = self.collection.update_one(
            {'_id': ObjectId(content_id), 'user_id': user_id},
            {'$set': updates}
        )
        
        return result.modified_count > 0
    
    def delete_content(self, content_id, user_id):
        """Delete content"""
        result = self.collection.delete_one({
            '_id': ObjectId(content_id),
            'user_id': user_id
        })
        
        return result.deleted_count > 0
    
    def close_connection(self):
        """Close database connection"""
        self.client.close()
