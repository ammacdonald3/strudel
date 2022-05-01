import boto3
from flask import current_app

# Function to upload a file to an S3 bucket
def upload_file(file_name, bucket, new_file_name):
    # Note:
    # 'file_name' variable is the actual file being uploaded
    # 'new_file_name' variable is the new randomized name being assigned to the uploaded file
    url = None

    # Establish session with AWS
    session = boto3.Session(aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'], aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'])
    s3_client = session.client('s3')
    
    # Upload file to AWS bucket
    try:
        s3_client.upload_fileobj(
            file_name, bucket, new_file_name, ExtraArgs={'ACL': 'public-read'}
            )
        url = f'https://{bucket}.s3.amazonaws.com/{new_file_name}'

    except Exception as e:
        output = []
        output.append(str(e))
        print(output)

    return url