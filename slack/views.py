import hashlib
import hmac
import time
import json

from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from avanan.services import SQSService


@method_decorator(csrf_exempt, name='dispatch')
class SlackEventsView(View):

    def post(self, request, *args, **kwargs):
        slack_event = json.loads(request.body)
        if slack_event.get("challenge"):
            return JsonResponse({'challenge': slack_event['challenge']})
        is_verified, error = self.signature_verification()
        if not is_verified:
            return HttpResponseForbidden(error)
        event = slack_event.get('event', {})
        if event:
            if event['type'] == 'message':
                event_json = json.dumps(event)
                sqs_service = SQSService()
                sqs_service.send_message(event_json, event.get('client_msg_id'))
        return HttpResponse('OK', status=200)

    def signature_verification(self):
        slack_signature = self.request.headers.get('X-Slack-Signature')
        slack_request_timestamp = self.request.headers.get('X-Slack-Request-Timestamp')

        if abs(time.time() - int(slack_request_timestamp)) > 60 * 5:
            return False, 'Invalid timestamp'

        sig_basestring = f'v0:{slack_request_timestamp}:{self.request.body.decode("utf-8")}'
        my_signature = 'v0=' + hmac.new(
            bytes(settings.SLACK_SIGNING_SECRET, 'utf-8'),
            bytes(sig_basestring, 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(my_signature, slack_signature):
            return False, 'Invalid signature'
        return True, None
