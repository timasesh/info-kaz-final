from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    """Storage class for media files like uploads and summernote attachments."""
    location = 'media'
    file_overwrite = False
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    custom_domain = settings.AWS_S3_CDN_DOMAIN
    default_acl = 'public-read'    
    
    
    

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('access_key', settings.AWS_ACCESS_KEY_ID)
        kwargs.setdefault('secret_key', settings.AWS_SECRET_ACCESS_KEY)
        kwargs.setdefault('endpoint_url', settings.AWS_S3_ENDPOINT_URL)
        kwargs.setdefault('region_name', settings.AWS_S3_REGION_NAME)
        kwargs.setdefault('object_parameters', settings.AWS_S3_OBJECT_PARAMETERS)
        super().__init__(*args, **kwargs)   
 
    def _get_valid_path(self, name):
        """
        Ensure the path has the correct structure:
        - news-images/YYYY/MM/DD/filename for news images
        - {bucket_name}/media/uploads/... for other uploaded content
        """
        # Don't modify paths that are already absolute URLs
        if name.startswith('http://') or name.startswith('https://'):
            return name

        # Strip any leading slashes
        name = name.lstrip('/')
          # For news images, ensure media prefix is present
        if name.startswith(f'{self.bucket_name}/news-images/'):
            # Insert media/ after bucket name if missing
            parts = name.split('/', 1)
            return f'{parts[0]}/media/{parts[1]}'
        elif name.startswith('news-images/'):
            return f'{self.bucket_name}/media/{name}'
            
        # For all other uploads, ensure they're under bucket/media/uploads/
        if not name.startswith(f'{self.bucket_name}/media/'):
            name = name.replace('media/', '', 1)  # Remove any existing media/ prefix
            if name.startswith('uploads/'):
                name = f'{self.bucket_name}/media/{name}'
            else:
                name = f'{self.bucket_name}/media/uploads/{name}'
                
        return name

    
    def url(self, name, parameters=None, expire=None):
        """
        Generate the URL where the file can be accessed.
        Ensures the path has the correct structure and uses CDN domain.
        """
        # Don't modify paths that are already absolute URLs
        if name.startswith('http://') or name.startswith('https://'):
            return name
            
        name = self._get_valid_path(name)
        
        # Use CDN domain if available, otherwise use direct S3 endpoint
        if self.custom_domain:
            return f'https://{self.custom_domain}/{name}'
            
        return f'{self.endpoint_url}/{self.bucket_name}/{name}'

# For backwards compatibility with django-summernote migrations
class MediaRootS3BotoStorage(MediaStorage):
    pass
