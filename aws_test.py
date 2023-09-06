import boto3
import json

s3 = boto3.resource('s3')

for bucket in s3.buckets.all():
    print(bucket.name)

s3 = boto3.client('s3')
# s3.upload_file('./output_video1.mp4', 'knn12356', 'output_video1.mp4')

data = {
    'timestamp': '2020-05-01 12:00:00',
    'camera_id': '1',
    'frames': [
        [[[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1,2,3,4,5]],
        [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1,2,3,4,5]],
        [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1,2,3,4,5]]],
        [[[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1,2,3,4,5]],
        [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1,2,3,4,5]],
        [[1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1,2,3,4,5]]]
    ]
}

result = s3.put_object(Body=json.dumps(data), Bucket='knn12356', Key='test.json')

res = result.get('ResponseMetadata', {})

if res.get('HTTPStatusCode') == 200:
    print('Uploaded successfully')
else:
    print('Upload failed')
