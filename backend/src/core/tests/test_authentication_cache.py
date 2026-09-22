"""Provider signing-key caching and refresh, without live identity providers."""

import time
from typing import Any
from unittest.mock import AsyncMock, Mock, call

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from jwt.algorithms import RSAAlgorithm

from core.authentication import azure, base, linkedin

pytestmark = pytest.mark.anyio


@pytest.fixture
def signing_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    public_key.update(kid="new-key", use="sig", alg="RS256")
    claims = {
        "iss": "https://www.linkedin.com",
        "aud": "synthetic-client",
        "sub": "subject",
        "iat": int(time.time()) - 5,
        "exp": int(time.time()) + 300,
    }
    token = jwt.encode(
        claims, private_key, algorithm="RS256", headers={"kid": "new-key"}
    )
    return token, {"keys": [public_key]}


@pytest.fixture
def key_cache(monkeypatch):
    entries: dict[str, Any] = {}
    client = Mock()
    client.json.return_value.get.side_effect = entries.get

    def save(key, path, value):
        assert path == "."
        entries[key] = value
        return True

    client.json.return_value.set.side_effect = save
    monkeypatch.setattr(base, "redis_session_client", client)
    return entries, client


@pytest.mark.parametrize("provider", ["microsoft", "linkedin"])
@pytest.mark.parametrize(
    "cached,refresh", [(False, False), (True, False), (True, True)]
)
async def test_provider_key_cache(monkeypatch, key_cache, provider, cached, refresh):
    entries, client = key_cache
    key = f"jwks:{provider}"
    old_keys = {"keys": [{"kid": "old-key"}]}
    new_keys = {"keys": [{"kid": "new-key"}]}
    if cached:
        entries[key] = old_keys
    # Other providers' records must never be overwritten or used for validation.
    other_key = "jwks:linkedin" if provider == "microsoft" else "jwks:microsoft"
    entries[other_key] = {"keys": [{"kid": "other-provider"}]}
    response = Mock()
    response.json.return_value = new_keys
    discovery = Mock()
    discovery.json.return_value = {"jwks_uri": "https://microsoft.invalid/keys"}
    fetch = Mock(
        side_effect=[discovery, response] if provider == "microsoft" else [response]
    )
    monkeypatch.setattr(base.httpx2, "get", fetch)
    monkeypatch.setattr(
        azure.config, "AZURE_OPENID_CONFIG_URL", "https://microsoft.invalid/discovery"
    )
    loader = (
        azure.get_azure_jwks if provider == "microsoft" else linkedin.get_linkedin_jwks
    )
    result = await loader(no_cache=refresh)
    if cached and not refresh:
        assert result == old_keys
        fetch.assert_not_called()
        client.json.return_value.set.assert_not_called()
    else:
        assert result == new_keys
        assert entries[key] == new_keys
        if provider == "microsoft":
            assert fetch.call_args_list == [
                call("https://microsoft.invalid/discovery"),
                call("https://microsoft.invalid/keys"),
            ]
        else:
            fetch.assert_called_once_with(linkedin.LINKEDIN_JWKS_URL)
    assert entries[other_key] == {"keys": [{"kid": "other-provider"}]}
    if refresh:
        client.json.return_value.get.assert_not_called()


async def test_malformed_key_response_does_not_replace_cache(monkeypatch, key_cache):
    entries, client = key_cache
    entries["jwks:linkedin"] = {"keys": [{"kid": "existing-key"}]}
    response = Mock()
    response.json.return_value = {"unexpected": "response"}
    monkeypatch.setattr(base.httpx2, "get", Mock(return_value=response))
    with pytest.raises(HTTPException) as error:
        await linkedin.get_linkedin_jwks(no_cache=True)
    assert error.value.status_code == 502
    client.json.return_value.set.assert_not_called()
    assert entries["jwks:linkedin"]["keys"][0]["kid"] == "existing-key"


async def test_failed_key_refresh_is_not_cached(monkeypatch, key_cache):
    _, client = key_cache
    response = Mock()
    response.raise_for_status.side_effect = RuntimeError("provider unavailable")
    monkeypatch.setattr(base.httpx2, "get", Mock(return_value=response))
    with pytest.raises(RuntimeError, match="provider unavailable"):
        await linkedin.get_linkedin_jwks(no_cache=True)
    client.json.return_value.set.assert_not_called()


async def test_linkedin_key_rotation_refreshes_once(
    monkeypatch, key_cache, signing_keys
):
    entries, _ = key_cache
    token, current_keys = signing_keys
    entries["jwks:linkedin"] = {"keys": [{"kid": "retired-key"}]}
    response = Mock()
    response.json.return_value = current_keys
    fetch = Mock(return_value=response)
    monkeypatch.setattr(base.httpx2, "get", fetch)
    for _ in range(2):
        claims = await linkedin.get_linkedin_token_payload(
            token, issuer="https://www.linkedin.com", client_id="synthetic-client"
        )
        assert claims["sub"] == "subject"
    fetch.assert_called_once_with(linkedin.LINKEDIN_JWKS_URL)
    assert entries["jwks:linkedin"] == current_keys


async def test_linkedin_invalid_signature_still_rejected_after_refresh(
    monkeypatch, key_cache, signing_keys
):
    entries, _ = key_cache
    token, _ = signing_keys
    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = RSAAlgorithm.to_jwk(wrong_key.public_key(), as_dict=True)
    public_key.update(kid="new-key", use="sig", alg="RS256")
    entries["jwks:linkedin"] = {"keys": [public_key]}
    response = Mock()
    response.json.return_value = entries["jwks:linkedin"]
    fetch = Mock(return_value=response)
    monkeypatch.setattr(base.httpx2, "get", fetch)
    with pytest.raises(jwt.InvalidSignatureError):
        await linkedin.get_linkedin_token_payload(
            token, issuer="https://www.linkedin.com", client_id="synthetic-client"
        )
    fetch.assert_called_once()


async def test_azure_retains_one_refresh_retry(monkeypatch):
    loader = AsyncMock(return_value={"keys": []})
    decoder = AsyncMock(side_effect=[jwt.InvalidSignatureError(), {"oid": "subject"}])
    monkeypatch.setattr(azure, "get_azure_jwks", loader)
    monkeypatch.setattr(azure, "decode_token", decoder)
    assert await azure.get_azure_token_payload("synthetic-token") == {"oid": "subject"}
    assert loader.call_args_list == [call(), call(no_cache=True)]
    assert decoder.await_count == 2
