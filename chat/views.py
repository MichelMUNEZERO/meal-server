import json
import urllib.error
import urllib.request

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from meal_system.api_utils import json_error, json_success, parse_json_body, require_auth


MAX_MESSAGES = 30
MAX_MESSAGE_LENGTH = 4000
SYSTEM_PROMPT = (
    'You are the helpful customer support assistant inside Michel Events meal tracking. '
    'Help users understand their meal plan, attendance, and how to use this system. '
    'Be concise, friendly, and honest when you do not have access to specific account data.'
)


def _extract_text(payload):
    for item in payload.get('output', []):
        for content in item.get('content', []):
            if content.get('type') in ('output_text', 'text') and content.get('text'):
                return content['text']

    choices = payload.get('choices', [])
    if choices:
        message = choices[0].get('message', {})
        content = message.get('content')
        if isinstance(content, str):
            return content

    return None


@csrf_exempt
@require_auth()
def chat_view(request):
    if request.method != 'POST':
        return json_error('Method not allowed', status=405)

    api_key = getattr(settings, 'GROQ_API_KEY', '')
    if not api_key:
        return json_error('The customer support assistant is not configured yet', status=503)

    data = parse_json_body(request)
    incoming_messages = data.get('messages', [])
    if not isinstance(incoming_messages, list) or not incoming_messages:
        return json_error('At least one message is required')

    messages = []
    for message in incoming_messages[-MAX_MESSAGES:]:
        if not isinstance(message, dict) or message.get('role') not in ('user', 'assistant'):
            return json_error('Invalid message format')
        content = str(message.get('content', '')).strip()
        if not content or len(content) > MAX_MESSAGE_LENGTH:
            return json_error(f'Messages must be between 1 and {MAX_MESSAGE_LENGTH} characters')
        messages.append({'role': message['role'], 'content': content})

    payload = json.dumps({
        'model': settings.GROQ_MODEL,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            *messages,
        ],
    }).encode('utf-8')
    request = urllib.request.Request(
        'https://api.groq.com/openai/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8', errors='replace')
        if error.code == 401:
            return json_error('The Groq API key is invalid or expired', status=503)
        if error.code == 403:
            return json_error(
                'Groq rejected the request. Check that the API key and account access are active.',
                status=503,
            )
        return json_error(f'Groq request failed ({error.code}): {detail[:300]}', status=502)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return json_error('Groq is temporarily unavailable. Please try again.', status=502)

    reply = _extract_text(result)
    if not reply:
        return json_error('Groq returned an empty response', status=502)

    return json_success(reply=reply, model=settings.GROQ_MODEL)
