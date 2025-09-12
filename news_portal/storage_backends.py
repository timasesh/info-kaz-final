import os
import uuid
import requests
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible

@deconstructible
class SupabaseStorage(Storage):
    """Storage class for media files using Supabase Storage REST API via requests"""
    
    def __init__(self, bucket_name='media'):
        self.bucket_name = bucket_name
        self.supabase_url = settings.SUPABASE_URL.rstrip('/')
        self.supabase_key = settings.SUPABASE_ANON_KEY
    
    def _headers(self, content_type: str | None = None) -> dict:
        headers = {
            'Authorization': f'Bearer {self.supabase_key}',
            'apikey': self.supabase_key,
        }
        if content_type:
            headers['Content-Type'] = content_type
        return headers
    
    def _object_url(self, name: str) -> str:
        return f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{name}"
    
    def _public_url(self, name: str) -> str:
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"
    
    def _open(self, name, mode='rb'):
        try:
            resp = requests.get(self._public_url(name), timeout=30)
            resp.raise_for_status()
            return ContentFile(resp.content)
        except Exception as e:
            raise FileNotFoundError(f"File {name} not found in Supabase Storage: {e}")
    
    def _save(self, name, content):
        try:
            # Ensure unique name if already exists
            if self.exists(name):
                name = self._get_unique_name(name)
            # Read content bytes
            file_bytes = content.read()
            content.seek(0)
            content_type = getattr(content, 'content_type', None) or 'application/octet-stream'
            # Use upsert=false to avoid overwrite
            url = self._object_url(name) + '?upsert=false'
            resp = requests.post(url, headers=self._headers(content_type), data=file_bytes, timeout=60)
            if resp.status_code not in (200, 201):
                raise Exception(f"HTTP {resp.status_code}: {resp.text}")
            return name
        except Exception as e:
            raise Exception(f"Failed to save file {name} to Supabase Storage: {e}")
    
    def delete(self, name):
        try:
            resp = requests.delete(self._object_url(name), headers=self._headers(), timeout=30)
            if resp.status_code not in (200, 204):
                raise Exception(f"HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            raise Exception(f"Failed to delete file {name} from Supabase Storage: {e}")
    
    def exists(self, name):
        try:
            resp = requests.head(self._public_url(name), timeout=15)
            return resp.status_code == 200
        except:
            return False
    
    def listdir(self, path):
        # Optional; not critical for uploads. Return empty lists for simplicity.
        return [], []
    
    def size(self, name):
        try:
            resp = requests.head(self._public_url(name), timeout=15)
            if resp.status_code == 200:
                return int(resp.headers.get('Content-Length', '0'))
            return 0
        except:
            return 0
    
    def url(self, name):
        return self._public_url(name)
    
    def _get_unique_name(self, name):
        name_root, ext = os.path.splitext(name)
        return f"{name_root}_{uuid.uuid4().hex[:8]}{ext}"

# Main storage class
class MediaStorage(SupabaseStorage):
    """Storage class for media files like uploads and summernote attachments."""
    def __init__(self):
        super().__init__(bucket_name='media')

# For backwards compatibility with django-summernote migrations
class MediaRootS3BotoStorage(MediaStorage):
    pass
