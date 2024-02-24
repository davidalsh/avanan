from slack_sdk.errors import SlackApiError


async def channel_delete_message(channel_id, message_ts, client):
    try:
        response = await client.chat_delete(channel=channel_id, ts=message_ts)
        assert response["ok"]
        print(f"Deleted message from {channel_id} at {message_ts}")
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")
