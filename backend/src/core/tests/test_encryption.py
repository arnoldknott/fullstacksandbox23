"""Application encryption contract and startup key discovery."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from core.encryption import (
    ENVELOPE_VERSION,
    Encryption,
    EncryptionKey,
    EncryptionKeyring,
    load_key_vault_encryption_keyring,
    load_local_encryption_keyring,
)

KEY = bytes(range(32))
PREVIOUS_KEY = bytes(reversed(range(32)))
ANCIENT_KEY = b"B" * 32
KEY_BASE64 = "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8="
PREVIOUS_KEY_BASE64 = "Hx4dHBsaGRgXFhUUExIREA8ODQwLCgkIBwYFBAMCAQA="
ANCIENT_KEY_BASE64 = "QkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkI="
FIXTURE_VALUE = {
    "access_token": "secret-token",
    "account": {"homeAccountId": "fixture-user"},
}
FIXTURE_ENVELOPE = {
    "version": 1,
    "key-version": "fixture-v1",
    "nonce": "AAECAwQFBgcICQoL",
    "ciphertext": "PCC3eKaAsWjSNfjg1IdaV6Gl4leCHitRTAiO4HNLLJBgc82T2q9muk7fXYXn6k15jToP+DSi6r4drQh/cZuBm4JZ6w+gtFRDYSk=",
    "tag": "8i6o1+OdlhyE1j8+1nQH3w==",
}


@pytest.fixture(autouse=True)
def run_migrations():
    """Override the application fixture; these are database-free unit tests."""
    yield


def encryption(
    *,
    current_version: str = "current",
    current_key: bytes = KEY,
    historical: tuple[EncryptionKey, ...] = (),
) -> Encryption:
    return Encryption(
        EncryptionKeyring(
            keys=(EncryptionKey(current_version, current_key), *historical),
        )
    )


def test_cross_runtime_fixture_decrypts() -> None:
    fixture = encryption(current_version="fixture-v1")
    assert fixture.decrypt("msal:fixture-user", "$", FIXTURE_ENVELOPE) == FIXTURE_VALUE


def test_current_and_all_historical_keys_round_trip() -> None:
    previous_writer = encryption(current_version="previous", current_key=PREVIOUS_KEY)
    ancient_writer = encryption(current_version="ancient", current_key=ANCIENT_KEY)
    previous_envelope = previous_writer.encrypt(
        "linkedin:subject", "$", {"idToken": "previous"}
    )
    ancient_envelope = ancient_writer.encrypt(
        "linkedin:subject", "$", {"idToken": "ancient"}
    )
    reader = encryption(
        historical=(
            EncryptionKey("previous", PREVIOUS_KEY),
            EncryptionKey("ancient", ANCIENT_KEY),
        )
    )

    assert reader.decrypt("linkedin:subject", "$", previous_envelope) == {
        "idToken": "previous"
    }
    assert reader.decrypt("linkedin:subject", "$", ancient_envelope) == {
        "idToken": "ancient"
    }


@pytest.mark.parametrize("field", ["nonce", "ciphertext", "tag"])
def test_modified_envelope_is_rejected(field: str) -> None:
    envelope = deepcopy(FIXTURE_ENVELOPE)
    encoded = envelope[field]
    envelope[field] = ("A" if encoded[0] != "A" else "B") + encoded[1:]
    with pytest.raises(ValueError, match="authentication failed|nonce"):
        encryption(current_version="fixture-v1").decrypt(
            "msal:fixture-user", "$", envelope
        )


@pytest.mark.parametrize(
    "location,purpose",
    [("msal:another-user", "$"), ("msal:fixture-user", "$.moved")],
)
def test_changed_associated_data_is_rejected(location: str, purpose: str) -> None:
    with pytest.raises(ValueError, match="authentication failed"):
        encryption(current_version="fixture-v1").decrypt(
            location, purpose, FIXTURE_ENVELOPE
        )


def test_unknown_version_and_malformed_envelopes_never_fall_back() -> None:
    unknown = {**FIXTURE_ENVELOPE, "key-version": "unknown"}
    malformed = dict(FIXTURE_ENVELOPE)
    malformed.pop("tag")
    reader = encryption(current_version="fixture-v1")
    with pytest.raises(ValueError, match="Unknown"):
        reader.decrypt("msal:fixture-user", "$", unknown)
    with pytest.raises(ValueError, match="Malformed"):
        reader.decrypt("msal:fixture-user", "$", malformed)


def test_unencrypted_values_are_rejected() -> None:
    with pytest.raises(ValueError, match="Unencrypted"):
        encryption().decrypt("linkedin:subject", "$", {"idToken": "legacy"})


def test_empty_keyrings_and_missing_local_keys_are_rejected() -> None:
    with pytest.raises(ValueError, match="At least one encryption key"):
        EncryptionKeyring(keys=())
    with pytest.raises(ValueError, match="At least one local encryption key"):
        load_local_encryption_keyring({})


def test_local_configuration_loads_three_ordered_keys() -> None:
    keyring = load_local_encryption_keyring(
        {
            "ENCRYPTION_KEY_1": KEY_BASE64,
            "ENCRYPTION_KEY_VERSION_1": "current",
            "ENCRYPTION_KEY_2": PREVIOUS_KEY_BASE64,
            "ENCRYPTION_KEY_VERSION_2": "previous",
            "ENCRYPTION_KEY_3": ANCIENT_KEY_BASE64,
            "ENCRYPTION_KEY_VERSION_3": "ancient",
        }
    )
    assert keyring.keys == (
        EncryptionKey("current", KEY),
        EncryptionKey("previous", PREVIOUS_KEY),
        EncryptionKey("ancient", ANCIENT_KEY),
    )


@pytest.mark.parametrize(
    "environment",
    [
        {"ENCRYPTION_KEY_1": "invalid", "ENCRYPTION_KEY_VERSION_1": "v1"},
        {"ENCRYPTION_KEY_1": KEY_BASE64},
        {"ENCRYPTION_KEY_1": "YQ==", "ENCRYPTION_KEY_VERSION_1": "v1"},
        {
            "ENCRYPTION_KEY_1": KEY_BASE64,
            "ENCRYPTION_KEY_VERSION_1": "v1",
            "ENCRYPTION_KEY_3": ANCIENT_KEY_BASE64,
            "ENCRYPTION_KEY_VERSION_3": "v3",
        },
    ],
)
def test_malformed_local_configuration_fails(environment: dict[str, str]) -> None:
    with pytest.raises(ValueError):
        load_local_encryption_keyring(environment)


def secret(version: str, value: str, created_on: datetime, enabled: bool = True):
    properties = SimpleNamespace(
        version=version, created_on=created_on, enabled=enabled
    )
    return SimpleNamespace(value=value, properties=properties)


def vault_client(
    latest_versions: list[str],
    versions: list[object],
    values: dict[str, object],
) -> Mock:
    client = Mock()
    latest = iter(latest_versions)

    def get_secret(_name: str, version: str | None = None):
        selected = version if version is not None else next(latest)
        selected_secret = values[selected]
        if isinstance(selected_secret, Exception):
            raise selected_secret
        return selected_secret

    client.get_secret.side_effect = get_secret
    client.list_properties_of_secret_versions.side_effect = lambda _name: iter(versions)
    return client


def test_key_vault_loads_every_version_in_creation_order() -> None:
    now = datetime.now(timezone.utc)
    ancient = secret("ancient", ANCIENT_KEY_BASE64, now - timedelta(days=2))
    previous = secret("previous", PREVIOUS_KEY_BASE64, now - timedelta(days=1))
    current = secret("current", KEY_BASE64, now)
    client = vault_client(
        ["current", "current"],
        [previous.properties, ancient.properties, current.properties],
        {"current": current, "previous": previous, "ancient": ancient},
    )

    keyring = load_key_vault_encryption_keyring(client)

    assert keyring.keys == (
        EncryptionKey("current", KEY),
        EncryptionKey("previous", PREVIOUS_KEY),
        EncryptionKey("ancient", ANCIENT_KEY),
    )
    assert client.get_secret.call_count == 4


def test_key_vault_first_generation_and_startup_rotation_race() -> None:
    now = datetime.now(timezone.utc)
    previous = secret("previous", PREVIOUS_KEY_BASE64, now - timedelta(days=1))
    current = secret("current", KEY_BASE64, now)
    client = vault_client(
        ["current", "current"], [current.properties], {"current": current}
    )
    assert load_key_vault_encryption_keyring(client).keys == (
        EncryptionKey("current", KEY),
    )

    client = vault_client(
        ["previous", "current", "current"],
        [previous.properties, current.properties],
        {"current": current, "previous": previous},
    )
    assert load_key_vault_encryption_keyring(client).keys == (
        EncryptionKey("current", KEY),
        EncryptionKey("previous", PREVIOUS_KEY),
    )
    assert client.list_properties_of_secret_versions.call_count == 2


def test_key_vault_rejects_ambiguous_disabled_or_unavailable_history() -> None:
    now = datetime.now(timezone.utc)
    current = secret("current", KEY_BASE64, now)
    ambiguous = secret("ambiguous", PREVIOUS_KEY_BASE64, now)
    client = vault_client(
        ["current"],
        [current.properties, ambiguous.properties],
        {"current": current, "ambiguous": ambiguous},
    )
    with pytest.raises(ValueError, match="ambiguous"):
        load_key_vault_encryption_keyring(client)

    disabled = secret(
        "disabled", PREVIOUS_KEY_BASE64, now - timedelta(days=1), enabled=False
    )
    client = vault_client(
        ["current"],
        [current.properties, disabled.properties],
        {"current": current, "disabled": disabled},
    )
    with pytest.raises(ValueError, match="disabled"):
        load_key_vault_encryption_keyring(client)

    unavailable = secret("unavailable", PREVIOUS_KEY_BASE64, now - timedelta(days=1))
    client = vault_client(
        ["current"],
        [current.properties, unavailable.properties],
        {"current": current, "unavailable": RuntimeError("unavailable")},
    )
    with pytest.raises(RuntimeError, match="unavailable"):
        load_key_vault_encryption_keyring(client)


def test_key_vault_does_not_hide_list_permission_failures() -> None:
    current = secret("current", KEY_BASE64, datetime.now(timezone.utc))
    client = Mock()
    client.get_secret.return_value = current
    client.list_properties_of_secret_versions.side_effect = PermissionError("denied")
    with pytest.raises(PermissionError, match="denied"):
        load_key_vault_encryption_keyring(client)


def test_envelope_format_version_is_stable() -> None:
    assert ENVELOPE_VERSION == 1
