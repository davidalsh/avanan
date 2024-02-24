import os
import re

import django
from aiobotocore.session import get_session
import asyncio
import json

from asgiref.sync import sync_to_async
from django.conf import settings
from slack_sdk.web.async_client import AsyncWebClient

from slack.api.slack_web_client import channel_delete_message

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'avanan.settings')
django.setup()

from dlp.models import DLPPattern
from slack.models import FlaggedMessage


class Manager:

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.session = get_session()
        self.queue_url = None

    async def setup(self):
        async with self.session.create_client('sqs', region_name=settings.AWS_REGION,
                                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID) as client:
            response = await client.get_queue_url(QueueName=settings.AWS_QUEUE_NAME)
            self.queue_url = response['QueueUrl']

    async def get_patterns(self):
        return await sync_to_async(self._get_patterns_sync)()

    def _get_patterns_sync(self):
        return list(DLPPattern.objects.values_list('id', 'pattern'))

    async def _get_messages(self, client):
        messages = await client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10,
            VisibilityTimeout=180,
        )

        return messages.get('Messages', [])

    async def process_messages(self, messages, client):
        patterns = await self.get_patterns()
        for message in messages:
            print('Message:', message)
            event = json.loads(message['Body'])
            text = event.get('text', '')

            if text:
                for pattern_id, pattern in patterns:
                    match = re.search(fr'{pattern}', text)
                    if match:
                        channel = event.get('channel')
                        ts = event.get('ts')
                        kwargs = {
                            'client_msg_id': event.get('client_msg_id'),
                            'ts': ts,
                            'type': 'MSG' if event.get('type') == 'message' else 'FILE',
                            'text': event.get('text'),
                            'user': event.get('user'),
                            'team': event.get('team'),
                            'channel': channel,
                            'pattern_id': pattern_id,
                        }
                        await sync_to_async(FlaggedMessage.objects.create)(**kwargs)
                        slack_client = AsyncWebClient(token=settings.SLACK_BOT_USER_OAUTH_TOKEN)
                        await channel_delete_message(channel, ts, slack_client)
                        break

            await self.delete_message(message['ReceiptHandle'], client)

    async def delete_message(self, receipt_handle, client):
        await client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )

    async def main(self):
        await self.setup()
        async with self.session.create_client('sqs', region_name=settings.AWS_REGION,
                                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID) as client:
            while True:
                messages = await self._get_messages(client)
                await self.process_messages(messages, client)
                await asyncio.sleep(1)
