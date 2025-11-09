import os
import boto3
import pickle
import json
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError, NoCredentialsError
import logging

# Setup logging
logger = logging.getLogger(__name__)

class S3Manager:
    """AWS S3 utility class for model storage and retrieval"""
    
    def __init__(self, bucket_name: str = None, region: str = None):
        """
        Initialize S3 manager
        
        Args:
            bucket_name: S3 bucket name (defaults to environment variable)
            region: AWS region (defaults to environment variable)
        """
        self.bucket_name = bucket_name or os.getenv('S3_BUCKET', 'news-intelligence-models')
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        
        try:
            self.s3_client = boto3.client('s3', region_name=self.region)
            self.s3_resource = boto3.resource('s3', region_name=self.region)
            logger.info(f"S3 manager initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.warning("AWS credentials not found. S3 operations will be disabled.")
            self.s3_client = None
            self.s3_resource = None
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None
            self.s3_resource = None
    
    def is_available(self) -> bool:
        """Check if S3 is available"""
        return self.s3_client is not None
    
    def _ensure_bucket_exists(self):
        """Create S3 bucket if it doesn't exist"""
        if not self.is_available():
            return
        
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.info(f"Bucket '{self.bucket_name}' not found. Creating it...")
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    logger.info(f"Bucket '{self.bucket_name}' created successfully.")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket '{self.bucket_name}': {create_error}")
                    raise
            else:
                logger.error(f"Error checking for bucket '{self.bucket_name}': {e}")
                raise

    def upload_file(self, local_path: str, s3_key: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Upload file to S3
        
        Args:
            local_path: Local file path
            s3_key: S3 object key
            metadata: Optional metadata to attach to the object
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("S3 is not available")
            return False
        
        try:
            self._ensure_bucket_exists()  # Ensure bucket exists before upload
            
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
            logger.info(f"File uploaded to S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            return False
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Download file from S3
        
        Args:
            s3_key: S3 object key
            local_path: Local file path
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("S3 is not available")
            return False
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"File downloaded from S3: {s3_key}")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"S3 object not found: {s3_key}")
            else:
                logger.error(f"Failed to download file from S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading from S3: {e}")
            return False
    
    def upload_object(self, obj: Any, s3_key: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Upload Python object to S3 (pickled)
        
        Args:
            obj: Python object to upload
            s3_key: S3 object key
            metadata: Optional metadata to attach to the object
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("S3 is not available")
            return False
        
        try:
            # Pickle the object
            pickled_data = pickle.dumps(obj)
            
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=pickled_data,
                **extra_args
            )
            logger.info(f"Object uploaded to S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload object to S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading object to S3: {e}")
            return False
    
    def download_object(self, s3_key: str) -> Optional[Any]:
        """
        Download Python object from S3 (unpickled)
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Python object if successful, None otherwise
        """
        if not self.is_available():
            logger.error("S3 is not available")
            return None
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            pickled_data = response['Body'].read()
            obj = pickle.loads(pickled_data)
            logger.info(f"Object downloaded from S3: {s3_key}")
            return obj
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"S3 object not found: {s3_key}")
            else:
                logger.error(f"Failed to download object from S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading object from S3: {e}")
            return None
    
    def upload_json(self, data: Dict[str, Any], s3_key: str) -> bool:
        """
        Upload JSON data to S3
        
        Args:
            data: Dictionary to upload as JSON
            s3_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("S3 is not available")
            return False
        
        try:
            json_data = json.dumps(data, default=str)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            logger.info(f"JSON data uploaded to S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload JSON to S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading JSON to S3: {e}")
            return False
    
    def download_json(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """
        Download JSON data from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Dictionary if successful, None otherwise
        """
        if not self.is_available():
            logger.error("S3 is not available")
            return None
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            json_data = response['Body'].read().decode('utf-8')
            data = json.loads(json_data)
            logger.info(f"JSON data downloaded from S3: {s3_key}")
            return data
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.warning(f"S3 object not found: {s3_key}")
            else:
                logger.error(f"Failed to download JSON from S3: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading JSON from S3: {e}")
            return None
    
    def list_objects(self, prefix: str = '') -> List[str]:
        """
        List objects in S3 bucket
        
        Args:
            prefix: Object key prefix to filter by
            
        Returns:
            List of object keys
        """
        if not self.is_available():
            logger.error("S3 is not available")
            return []
        
        try:
            objects = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                if 'Contents' in page:
                    objects.extend([obj['Key'] for obj in page['Contents']])
            
            logger.info(f"Listed {len(objects)} objects from S3 with prefix '{prefix}'")
            return objects
            
        except ClientError as e:
            logger.error(f"Failed to list objects from S3: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing objects from S3: {e}")
            return []
    
    def delete_object(self, s3_key: str) -> bool:
        """
        Delete object from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.error("S3 is not available")
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Object deleted from S3: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete object from S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting object from S3: {e}")
            return False
    
    def object_exists(self, s3_key: str) -> bool:
        """
        Check if object exists in S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if exists, False otherwise
        """
        if not self.is_available():
            logger.error("S3 is not available")
            return False
        
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Failed to check object existence in S3: {e}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error checking object existence in S3: {e}")
            return False

class ModelManager:
    """Manager for handling ML model storage and retrieval"""
    
    def __init__(self, s3_manager: S3Manager = None):
        """
        Initialize model manager
        
        Args:
            s3_manager: S3Manager instance (creates new one if None)
        """
        self.s3_manager = s3_manager or S3Manager()
        self.local_cache = {}
    
    def save_model(self, model: Any, model_name: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Save model to S3
        
        Args:
            model: Model object to save
            model_name: Name of the model
            metadata: Optional metadata
            
        Returns:
            True if successful, False otherwise
        """
        s3_key = f"models/{model_name}.pkl"
        
        # Add metadata
        model_metadata = metadata or {}
        model_metadata.update({
            'model_name': model_name,
            'save_timestamp': datetime.utcnow().isoformat(),
            'model_type': type(model).__name__
        })
        
        return self.s3_manager.upload_object(model, s3_key, model_metadata)
    
    def load_model(self, model_name: str, use_cache: bool = True) -> Optional[Any]:
        """
        Load model from S3
        
        Args:
            model_name: Name of the model
            use_cache: Whether to use local cache
            
        Returns:
            Model object if successful, None otherwise
        """
        if use_cache and model_name in self.local_cache:
            logger.info(f"Using cached model: {model_name}")
            return self.local_cache[model_name]
        
        s3_key = f"models/{model_name}.pkl"
        model = self.s3_manager.download_object(s3_key)
        
        if model and use_cache:
            self.local_cache[model_name] = model
        
        return model
    
    def save_vectorizer(self, vectorizer: Any, vectorizer_name: str) -> bool:
        """
        Save vectorizer to S3
        
        Args:
            vectorizer: Vectorizer object to save
            vectorizer_name: Name of the vectorizer
            
        Returns:
            True if successful, False otherwise
        """
        s3_key = f"vectorizers/{vectorizer_name}.pkl"
        metadata = {
            'vectorizer_name': vectorizer_name,
            'save_timestamp': datetime.utcnow().isoformat(),
            'vectorizer_type': type(vectorizer).__name__
        }
        
        return self.s3_manager.upload_object(vectorizer, s3_key, metadata)
    
    def load_vectorizer(self, vectorizer_name: str, use_cache: bool = True) -> Optional[Any]:
        """
        Load vectorizer from S3
        
        Args:
            vectorizer_name: Name of the vectorizer
            use_cache: Whether to use local cache
            
        Returns:
            Vectorizer object if successful, None otherwise
        """
        if use_cache and vectorizer_name in self.local_cache:
            logger.info(f"Using cached vectorizer: {vectorizer_name}")
            return self.local_cache[vectorizer_name]
        
        s3_key = f"vectorizers/{vectorizer_name}.pkl"
        vectorizer = self.s3_manager.download_object(s3_key)
        
        if vectorizer and use_cache:
            self.local_cache[vectorizer_name] = vectorizer
        
        return vectorizer
    
    def list_models(self) -> List[str]:
        """List all models in S3"""
        model_objects = self.s3_manager.list_objects('models/')
        return [obj.replace('models/', '').replace('.pkl', '') for obj in model_objects if obj.endswith('.pkl')]
    
    def list_vectorizers(self) -> List[str]:
        """List all vectorizers in S3"""
        vectorizer_objects = self.s3_manager.list_objects('vectorizers/')
        return [obj.replace('vectorizers/', '').replace('.pkl', '') for obj in vectorizer_objects if obj.endswith('.pkl')]
    
    def delete_model(self, model_name: str) -> bool:
        """Delete model from S3"""
        s3_key = f"models/{model_name}.pkl"
        return self.s3_manager.delete_object(s3_key)
    
    def delete_vectorizer(self, vectorizer_name: str) -> bool:
        """Delete vectorizer from S3"""
        s3_key = f"vectorizers/{vectorizer_name}.pkl"
        return self.s3_manager.delete_object(s3_key)
    
    def clear_cache(self):
        """Clear local cache"""
        self.local_cache.clear()
        logger.info("Local cache cleared")

# Utility functions
def upload_model_to_s3(model: Any, model_name: str, bucket_name: str = None, metadata: Dict[str, Any] = None) -> bool:
    """
    Convenience function to upload a model to S3
    
    Args:
        model: Model object to upload
        model_name: Name of the model
        bucket_name: S3 bucket name (optional)
        metadata: Optional metadata
        
    Returns:
        True if successful, False otherwise
    """
    manager = ModelManager(S3Manager(bucket_name))
    return manager.save_model(model, model_name, metadata)

def download_model_from_s3(model_name: str, bucket_name: str = None) -> Optional[Any]:
    """
    Convenience function to download a model from S3
    
    Args:
        model_name: Name of the model
        bucket_name: S3 bucket name (optional)
        
    Returns:
        Model object if successful, None otherwise
    """
    manager = ModelManager(S3Manager(bucket_name))
    return manager.load_model(model_name)

if __name__ == "__main__":
    # Test S3 functionality
    print("Testing S3 utilities...")
    
    # Test S3 manager
    s3_manager = S3Manager()
    
    if s3_manager.is_available():
        print("S3 is available")
        
        # Test JSON upload/download
        test_data = {'test': 'data', 'timestamp': '2024-01-01'}
        test_key = 'test/test_data.json'
        
        if s3_manager.upload_json(test_data, test_key):
            print("JSON upload successful")
            
            downloaded_data = s3_manager.download_json(test_key)
            if downloaded_data:
                print(f"JSON download successful: {downloaded_data}")
            
            # Clean up
            s3_manager.delete_object(test_key)
        
        # Test model manager
        model_manager = ModelManager(s3_manager)
        
        # Test with a simple object
        test_model = {'type': 'test_model', 'version': '1.0'}
        
        if model_manager.save_model(test_model, 'test_model'):
            print("Model upload successful")
            
            loaded_model = model_manager.load_model('test_model')
            if loaded_model:
                print(f"Model download successful: {loaded_model}")
            
            # Clean up
            model_manager.delete_model('test_model')
    else:
        print("S3 is not available (credentials not configured)")
    
    print("S3 utility test completed")