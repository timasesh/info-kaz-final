import os
import uuid
from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
from supabase import create_client, Client

@deconstructible
class SupabaseStorage(Storage):
    """Storage class for media files using Supabase Storage API"""
    
    def __init__(self, bucket_name='media'):
        self.bucket_name = bucket_name
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_ANON_KEY
        self._client = None
    
    @property
    def client(self) -> Client:
        """Lazy initialization of Supabase client"""
        if self._client is None:
            self._client = create_client(self.supabase_url, self.supabase_key)
        return self._client
    
    def _open(self, name, mode='rb'):
        """Open file for reading"""
        try:
            response = self.client.storage.from_(self.bucket_name).download(name)
            return ContentFile(response)
        except Exception as e:
            raise FileNotFoundError(f"File {name} not found in Supabase Storage: {e}")
    
    def _save(self, name, content):
        """Save file to Supabase Storage"""
        try:
            # Generate unique filename if file already exists
            if self.exists(name):
                name = self._get_unique_name(name)
            
            # Upload file to Supabase
            response = self.client.storage.from_(self.bucket_name).upload(
                name, 
                content.read(),
                file_options={"content-type": content.content_type or "application/octet-stream"}
            )
            
            # Reset file pointer
            content.seek(0)
            return name
        except Exception as e:
            raise Exception(f"Failed to save file {name} to Supabase Storage: {e}")
    
    def delete(self, name):
        """Delete file from Supabase Storage"""
        try:
            self.client.storage.from_(self.bucket_name).remove([name])
        except Exception as e:
            raise Exception(f"Failed to delete file {name} from Supabase Storage: {e}")
    
    def exists(self, name):
        """Check if file exists in Supabase Storage"""
        try:
            files = self.client.storage.from_(self.bucket_name).list()
            return any(file['name'] == name for file in files)
        except:
            return False
    
    def listdir(self, path):
        """List directory contents"""
        try:
            files = self.client.storage.from_(self.bucket_name).list(path)
            directories = []
            file_list = []
            
            for file in files:
                if file.get('metadata', {}).get('mimetype') == 'application/folder':
                    directories.append(file['name'])
                else:
                    file_list.append(file['name'])
            
            return directories, file_list
        except:
            return [], []
    
    def size(self, name):
        """Get file size"""
        try:
            files = self.client.storage.from_(self.bucket_name).list()
            for file in files:
                if file['name'] == name:
                    return file.get('metadata', {}).get('size', 0)
            return 0
        except:
            return 0
    
    def url(self, name):
        """Get public URL for file"""
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{name}"
    
    def _get_unique_name(self, name):
        """Generate unique filename"""
        name, ext = os.path.splitext(name)
        return f"{name}_{uuid.uuid4().hex[:8]}{ext}"

# Main storage class
class MediaStorage(SupabaseStorage):
    """Storage class for media files like uploads and summernote attachments."""
    def __init__(self):
        super().__init__(bucket_name='media')

# For backwards compatibility with django-summernote migrations
class MediaRootS3BotoStorage(MediaStorage):
    pass
