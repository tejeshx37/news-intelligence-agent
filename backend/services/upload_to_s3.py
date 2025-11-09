#!/usr/bin/env python3
"""
Upload models and data to S3 storage
This script handles uploading trained models and related files to AWS S3
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.aws_utils import S3Manager, ModelManager
from utils.logger import setup_logging, StructuredLogger
from utils.config import Config

def setup_logging():
    """Setup logging configuration"""
    logger = setup_logging(
        log_level='INFO',
        enable_cloudwatch=False  # Disable CloudWatch for local uploads
    )
    return StructuredLogger(logger, 's3_upload')

def validate_model_files(model_dir: Path) -> Dict[str, bool]:
    """
    Validate that required model files exist
    
    Args:
        model_dir: Directory containing model files
        
    Returns:
        Dictionary mapping file names to existence status
    """
    required_files = {
        'sentiment_model.pkl': model_dir / 'sentiment_model.pkl',
        'vectorizer.pkl': model_dir / 'vectorizer.pkl',
        'fake_news_model.pkl': model_dir / 'fake_news_model.pkl',
        'fake_vectorizer.pkl': model_dir / 'fake_vectorizer.pkl'
    }
    
    file_status = {}
    for file_name, file_path in required_files.items():
        exists = file_path.exists()
        file_status[file_name] = exists
        
        if exists:
            logger.info(f"✓ Found {file_name} ({file_path.stat().st_size / 1024:.1f} KB)")
        else:
            logger.warning(f"✗ Missing {file_name} at {file_path}")
    
    return file_status

def upload_models_to_s3(s3_manager: S3Manager, model_dir: Path, file_status: Dict[str, bool]) -> Dict[str, bool]:
    """
    Upload model files to S3
    
    Args:
        s3_manager: S3Manager instance
        model_dir: Directory containing model files
        file_status: Dictionary of file existence status
        
    Returns:
        Dictionary mapping upload operations to success status
    """
    upload_results = {}
    
    # Define upload mappings
    upload_mappings = {
        'sentiment_model.pkl': 'models/sentiment_model.pkl',
        'vectorizer.pkl': 'vectorizers/sentiment_vectorizer.pkl',
        'fake_news_model.pkl': 'models/fake_news_model.pkl',
        'fake_vectorizer.pkl': 'vectorizers/fake_news_vectorizer.pkl'
    }
    
    for local_file, s3_key in upload_mappings.items():
        if file_status.get(local_file, False):
            local_path = model_dir / local_file
            
            # Add metadata
            metadata = {
                'model_type': 'sentiment' if 'sentiment' in s3_key else 'fake_news',
                'component_type': 'model' if 'model' in s3_key else 'vectorizer',
                'upload_timestamp': str(pd.Timestamp.now()),
                'file_size': str(local_path.stat().st_size),
                'original_filename': local_file
            }
            
            logger.info(f"Uploading {local_file} to s3://{s3_manager.bucket_name}/{s3_key}")
            
            success = s3_manager.upload_file(str(local_path), s3_key, metadata)
            upload_results[local_file] = success
            
            if success:
                logger.info(f"✓ Successfully uploaded {local_file}")
            else:
                logger.error(f"✗ Failed to upload {local_file}")
        else:
            logger.warning(f"Skipping {local_file} - file not found")
            upload_results[local_file] = False
    
    return upload_results

def upload_additional_files(s3_manager: S3Manager, additional_files: List[str]) -> Dict[str, bool]:
    """
    Upload additional files to S3
    
    Args:
        s3_manager: S3Manager instance
        additional_files: List of additional file paths to upload
        
    Returns:
        Dictionary mapping file paths to upload success status
    """
    upload_results = {}
    
    for file_path in additional_files:
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"Additional file not found: {file_path}")
            upload_results[str(file_path)] = False
            continue
        
        # Determine S3 key based on file type
        if file_path.suffix == '.pkl':
            s3_key = f"models/{file_path.name}"
        elif file_path.suffix == '.json':
            s3_key = f"config/{file_path.name}"
        elif file_path.suffix == '.csv':
            s3_key = f"data/{file_path.name}"
        else:
            s3_key = f"misc/{file_path.name}"
        
        logger.info(f"Uploading additional file: {file_path} to s3://{s3_manager.bucket_name}/{s3_key}")
        
        metadata = {
            'upload_timestamp': str(pd.Timestamp.now()),
            'file_size': str(file_path.stat().st_size),
            'original_filename': file_path.name
        }
        
        success = s3_manager.upload_file(str(file_path), s3_key, metadata)
        upload_results[str(file_path)] = success
        
        if success:
            logger.info(f"✓ Successfully uploaded {file_path.name}")
        else:
            logger.error(f"✗ Failed to upload {file_path.name}")
    
    return upload_results

def create_upload_manifest(upload_results: Dict[str, bool], additional_results: Dict[str, bool] = None) -> Dict[str, Any]:
    """
    Create manifest of uploaded files
    
    Args:
        upload_results: Results from model uploads
        additional_results: Results from additional file uploads
        
    Returns:
        Manifest dictionary
    """
    manifest = {
        'timestamp': str(pd.Timestamp.now()),
        'total_files': len(upload_results),
        'successful_uploads': sum(1 for success in upload_results.values() if success),
        'failed_uploads': sum(1 for success in upload_results.values() if not success),
        'model_files': upload_results
    }
    
    if additional_results:
        manifest['additional_files'] = additional_results
        manifest['total_files'] += len(additional_results)
        manifest['successful_uploads'] += sum(1 for success in additional_results.values() if success)
        manifest['failed_uploads'] += sum(1 for success in additional_results.values() if not success)
    
    return manifest

def upload_manifest_to_s3(s3_manager: S3Manager, manifest: Dict[str, Any]) -> bool:
    """
    Upload manifest to S3
    
    Args:
        s3_manager: S3Manager instance
        manifest: Manifest dictionary
        
    Returns:
        True if successful, False otherwise
    """
    import json
    import tempfile
    
    try:
        # Create temporary file for manifest
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(manifest, f, indent=2, default=str)
            temp_path = f.name
        
        s3_key = f"manifests/upload_manifest_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        logger.info(f"Uploading manifest to s3://{s3_manager.bucket_name}/{s3_key}")
        success = s3_manager.upload_file(temp_path, s3_key)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to upload manifest: {e}")
        return False

def main():
    """Main upload function"""
    global logger
    
    # Setup logging
    logger = setup_logging()
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Upload models and files to S3')
    parser.add_argument('--model-dir', type=str, default='model_training',
                       help='Directory containing model files (default: model_training)')
    parser.add_argument('--bucket', type=str, default=None,
                       help='S3 bucket name (default: from config)')
    parser.add_argument('--additional-files', type=str, nargs='*', default=[],
                       help='Additional files to upload')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip model file validation')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform dry run without actual uploads')
    parser.add_argument('--manifest', action='store_true',
                       help='Create and upload manifest file')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Starting S3 Upload Process")
    logger.info("=" * 60)
    
    try:
        # Initialize configuration
        config = Config()
        
        # Override bucket if specified
        bucket_name = args.bucket or config.get('S3_BUCKET', 'news-intelligence-models')
        
        logger.info(f"Target S3 bucket: {bucket_name}")
        logger.info(f"Model directory: {args.model_dir}")
        
        # Initialize S3 manager
        s3_manager = S3Manager(bucket_name=bucket_name)
        
        if not s3_manager.is_available():
            logger.error("S3 is not available. Check AWS credentials and configuration.")
            return 1
        
        # Validate model directory
        model_dir = Path(args.model_dir)
        if not model_dir.exists():
            logger.error(f"Model directory does not exist: {model_dir}")
            return 1
        
        # Validate model files
        if not args.skip_validation:
            logger.info("Validating model files...")
            file_status = validate_model_files(model_dir)
            
            if not any(file_status.values()):
                logger.error("No model files found. Please train models first.")
                return 1
        else:
            # Assume all files exist if validation is skipped
            file_status = {
                'sentiment_model.pkl': True,
                'vectorizer.pkl': True,
                'fake_news_model.pkl': True,
                'fake_vectorizer.pkl': True
            }
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No actual uploads will be performed")
            logger.info("Files that would be uploaded:")
            for file_name, exists in file_status.items():
                if exists:
                    logger.info(f"  - {file_name}")
            
            if args.additional_files:
                logger.info("Additional files:")
                for file_path in args.additional_files:
                    logger.info(f"  - {file_path}")
            
            return 0
        
        # Upload model files
        logger.info("Uploading model files to S3...")
        upload_results = upload_models_to_s3(s3_manager, model_dir, file_status)
        
        # Upload additional files
        additional_results = {}
        if args.additional_files:
            logger.info("Uploading additional files...")
            additional_results = upload_additional_files(s3_manager, args.additional_files)
        
        # Create and upload manifest
        if args.manifest:
            logger.info("Creating upload manifest...")
            manifest = create_upload_manifest(upload_results, additional_results)
            
            logger.info("Upload summary:")
            logger.info(f"  Total files: {manifest['total_files']}")
            logger.info(f"  Successful uploads: {manifest['successful_uploads']}")
            logger.info(f"  Failed uploads: {manifest['failed_uploads']}")
            
            upload_manifest_to_s3(s3_manager, manifest)
        
        # Final summary
        logger.info("=" * 60)
        logger.info("Upload Process Complete")
        logger.info("=" * 60)
        
        total_successful = sum(1 for success in upload_results.values() if success)
        total_additional = sum(1 for success in additional_results.values() if success) if additional_results else 0
        
        logger.info(f"Model files uploaded: {total_successful}/{len(upload_results)}")
        if additional_results:
            logger.info(f"Additional files uploaded: {total_additional}/{len(additional_results)}")
        
        if total_successful == 0:
            logger.warning("No model files were successfully uploaded")
            return 1
        
        logger.info("All uploads completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Upload process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error during upload process: {e}")
        logger.exception("Full traceback:")
        return 1

if __name__ == '__main__':
    # Import pandas for timestamp handling
    import pandas as pd
    from datetime import datetime
    
    sys.exit(main())