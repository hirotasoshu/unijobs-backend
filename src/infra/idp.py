from fastapi_keycloak_middleware import KeycloakConfiguration

idp_config = KeycloakConfiguration(
    url="http://127.0.0.1:8080/auth",
    client_id="unijobs-backend",
    client_secret="qVIHRPJWPqqzIanxDlWOFxBpv3K4qSeo",
    realm="unijobs",
    swagger_client_id="unijobs-backend",
)
