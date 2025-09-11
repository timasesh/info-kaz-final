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
    # Rely on django-storages default key handling and URL building.
    # With location='media' and custom_domain set, generated URLs will be:
    # https://<CDN_DOMAIN>/media/<path>

# For backwards compatibility with django-summernote migrations
class MediaRootS3BotoStorage(MediaStorage):
    pass
