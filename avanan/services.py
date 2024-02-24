import boto3
from botocore.exceptions import ClientError
from django.conf import settings


class SQSService:
    def __init__(self):
        self.sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.queue_url = self.get_queue_url()

    def get_queue_url(self):
        try:
            response = self.sqs_client.get_queue_url(QueueName=settings.AWS_QUEUE_NAME)
            return response['QueueUrl']
        except ClientError as e:
            print(f'Error fetching queue URL: {e}')
            return None

    def send_message(self, message_body, message_duplication_id=None):
        try:
            extra_kwargs = {}
            if message_duplication_id:
                extra_kwargs['MessageDeduplicationId'] = message_duplication_id
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=message_body,
                MessageGroupId='events_group',
                **extra_kwargs,
            )
            return response
        except ClientError as e:
            print(f'Error sending message: {e}')
            return None
