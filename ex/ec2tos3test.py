import boto3

s3 = boto3.resource('s3')

bucket_name = 'mobles3'
bucket = s3.Bucket(bucket_name)

# 파일 업로드하기
local_file ='/home/ubuntu/ec2tos3test.txt'
obj_file = 'normalvideo/ec2tos30411.txt'   # S3 에 올라갈 파일명
bucket.upload_file(local_file , obj_file)


print(f"{local_file} uploaded to s3://{bucket_name}/{obj_file}")