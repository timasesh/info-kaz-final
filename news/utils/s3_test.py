from django.conf import settings
import boto3

def test_s3_connection():
    """Test connection to DigitalOcean Spaces"""
    try:
        # Create an S3 client
        session = boto3.session.Session()
        client = session.client('s3',
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        # Try to list buckets
        response = client.list_buckets()
        print("S3 Connection successful!")
        print("Available buckets:", [bucket['Name'] for bucket in response['Buckets']])
        return True
    except Exception as e:
        print("Error connecting to S3:", str(e))
        return False
