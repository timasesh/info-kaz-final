from pathlib import Path
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
from ckeditor_uploader import utils
from PIL import Image
import os

def save_as(file, filepath):
    """Save uploaded file to storage and create thumbnail."""
    # Get the storage backend instance
    storage = default_storage
    bucket_name = getattr(storage, 'bucket_name', '')
      # Prepare the correct filepath
    clean_filepath = Path(filepath).name
    year = timezone.now().strftime('%Y')
    month = timezone.now().strftime('%m')
    day = timezone.now().strftime('%d')
    # Use news-images instead of uploads for better organization
    upload_path = f'news-app/media/news-images/{year}/{month}/{day}/{clean_filepath}'
    
    saved_path = storage.save(upload_path, file)
    create_thumbnail(file, saved_path)
    return saved_path

def create_thumbnail(file, saved_path):
    """Create and save thumbnail for image."""
    if not getattr(settings, "CKEDITOR_CREATE_THUMBNAIL", True):
        return

    THUMBNAIL_SIZE = getattr(settings, "CKEDITOR_THUMBNAIL_SIZE", (75, 75))
    storage = default_storage

    try:
        # Create thumbnail
        image = Image.open(file)
        image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
          # Generate thumbnail path, preserving the date structure
        parts = Path(saved_path).parts
        name = parts[-1]
        # Using the same path structure as the original file but adding .thumbs
        # Assuming path structure is news-app/media/news-images/YYYY/MM/DD/filename
        # Extract date parts from saved_path
        try:
            year, month, day = parts[-3:] if len(parts) >= 3 else (timezone.now().strftime('%Y'), timezone.now().strftime('%m'), timezone.now().strftime('%d'))
            # Keep the same path structure but add .thumbs
            thumbnail_filename = f'news-app/media/news-images/{year}/{month}/{day}/.thumbs/{name}'
        except:
            # Fallback if path structure is different
            year, month, day = timezone.now().strftime('%Y'), timezone.now().strftime('%m'), timezone.now().strftime('%d')
            thumbnail_filename = f'news-app/media/news-images/{year}/{month}/{day}/.thumbs/{name}'
        
        # Save to memory first
        from io import BytesIO
        thumb_io = BytesIO()
        image.save(thumb_io, format='JPEG', quality=90)
        thumb_io.seek(0)
        
        # Save to storage
        storage.save(thumbnail_filename, thumb_io)
        
    except (IOError, OSError) as e:
        print(f"Error creating thumbnail: {e}")
        return
