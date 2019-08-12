from pylti1p3.tool_config import ToolConfAbstract
from pylti1p3.registration import Registration
from pylti1p3.deployment import Deployment


TOOL_CONFIG = {
    "http://imsglobal.org": {
        "client_id": "pytest12345",
        "auth_login_url": "https://lti-ri.imsglobal.org/platforms/370/authorizations/new",
        "auth_token_url": "https://lti-ri.imsglobal.org/platforms/370/access_tokens",
        "key_set_url": "https://lti-ri.imsglobal.org/platforms/370/platform_keys/361.json",
        "key_set": None,
        "private_key_file": "private.key",
        "deployment": {
            "py1234": "py1234"
        }
    },
    "https://canvas.instructure.com": {
        "client_id": "10000000000004",
        "auth_login_url": "http://canvas.docker/api/lti/authorize_redirect",
        "auth_token_url": "http://canvas.docker/login/oauth2/token",
        "key_set_url": "http://canvas.docker/api/lti/security/jwks",
        "key_set": None,
        "private_key_file": "private.key",
        "deployment": {
            "6:8865aa05b4b79b64a91a86042e43af5ea8ae79eb": "6:8865aa05b4b79b64a91a86042e43af5ea8ae79eb"
        }
    }
}


class TestToolConf(ToolConfAbstract):

    def find_registration_by_issuer(self, iss):
        iss_conf = TOOL_CONFIG[iss]

        reg = Registration()
        return reg.set_auth_login_url(iss_conf['auth_login_url'])\
            .set_auth_token_url(iss_conf['auth_token_url'])\
            .set_client_id(iss_conf['client_id'])\
            .set_key_set(iss_conf['key_set'])\
            .set_key_set_url(iss_conf['key_set_url'])\
            .set_issuer(iss)\
            .set_tool_private_key(self._get_private_key())

    def find_deployment(self, iss, deployment_id):
        if deployment_id in TOOL_CONFIG[iss]['deployment']:
            return Deployment().set_deployment_id(TOOL_CONFIG[iss]['deployment'][deployment_id])
        return None

    def _get_private_key(self):
        return """-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
"""
