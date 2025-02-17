import sys
import time
import typing as t
import uuid
from bleach import clean

import jwt  # type: ignore

if t.TYPE_CHECKING:
    from .deep_link_resource import DeepLinkResource
    from .registration import Registration
    from typing_extensions import Literal
    from mypy_extensions import TypedDict

    _DeepLinkData = TypedDict(
        '_DeepLinkData',
        {
            # Required data:
            'deep_link_return_url': str,
            'accept_types': t.List[Literal['link', 'ltiResourceLink']],
            'accept_presentation_document_targets': t.List[
                Literal['iframe', 'window', 'embed']],

            # Optional data
            'accept_multiple': t.Union[bool, Literal['true', 'false']],
            'auto_create': t.Union[bool, Literal['true', 'false']],
            'title': str,
            'text': str,
            'data': object,
        },
        total=False,
    )


class DeepLink(object):
    _registration = None  # type: Registration
    _deployment_id = None  # type: str
    _deep_link_settings = None  # type: _DeepLinkData

    def __init__(self, registration, deployment_id, deep_link_settings):
        # type: (Registration, str, _DeepLinkData) -> None
        self._registration = registration
        self._deployment_id = deployment_id
        self._deep_link_settings = deep_link_settings

    def _generate_nonce(self):
        return uuid.uuid4().hex + uuid.uuid1().hex

    def get_message_jwt(self, resources):
        # type: (t.Sequence[DeepLinkResource]) -> t.Dict[str, object]
        message_jwt = {
            'iss': self._registration.get_client_id(),
            'aud': [self._registration.get_issuer()],
            'exp': int(time.time()) + 600,
            'iat': int(time.time()),
            'nonce': 'nonce-' + self._generate_nonce(),
            'https://purl.imsglobal.org/spec/lti/claim/deployment_id': self._deployment_id,
            'https://purl.imsglobal.org/spec/lti/claim/message_type': 'LtiDeepLinkingResponse',
            'https://purl.imsglobal.org/spec/lti/claim/version': '1.3.0',
            'https://purl.imsglobal.org/spec/lti-dl/claim/content_items': [r.to_dict() for r in resources],
            'https://purl.imsglobal.org/spec/lti-dl/claim/data': self._deep_link_settings.get('data')
        }
        return message_jwt

    def encode_jwt(self, message):
        headers = None
        kid = self._registration.get_kid()
        if kid:
            headers = {'kid': kid}
        encoded_jwt = jwt.encode(message, self._registration.get_tool_private_key(), algorithm='RS256',
                                 headers=headers)
        if sys.version_info[0] > 2 and isinstance(encoded_jwt, bytes):
            return encoded_jwt.decode('utf-8')
        return encoded_jwt

    def get_response_jwt(self, resources):
        # type: (t.Sequence[DeepLinkResource]) -> str
        message_jwt = self.get_message_jwt(resources)
        return self.encode_jwt(message_jwt)

    def get_response_form_html(self, jwt_val):
        # type: (str) -> str
        deep_link_return_url_sanitized = clean(self._deep_link_settings['deep_link_return_url'])
        html = '<form id="lti13_deep_link_auto_submit" action="%s" method="POST">' \
               '<input type="hidden" name="JWT" value="%s" /></form>' \
               '<script type="text/javascript">document.getElementById(\'lti13_deep_link_auto_submit\').submit();' \
               '</script>' % (deep_link_return_url_sanitized, jwt_val)
        return html

    def output_response_form(self, resources):
        # type: (t.List[DeepLinkResource]) -> str
        jwt_val = self.get_response_jwt(resources)
        return self.get_response_form_html(jwt_val)
