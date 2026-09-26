import base64
import binascii
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ENVELOPE_VERSION = 1
_ENVELOPE_FIELDS = {
    "version",
    "key-version",
    "nonce",
    "ciphertext",
    "tag",
}
_LOCAL_KEY_PATTERN = re.compile(r"^ENCRYPTION_KEY_(\d+)$")


@dataclass(frozen=True)
class EncryptionKey:
    version: str
    key: bytes

    def __post_init__(self) -> None:
        if not self.version or len(self.key) != 32:
            raise ValueError("Encryption keys require a version and 32 bytes.")


@dataclass(frozen=True)
class EncryptionKeyring:
    """Encryption keys ordered newest to oldest; index zero encrypts new data."""

    keys: tuple[EncryptionKey, ...]

    def __post_init__(self) -> None:
        if not self.keys:
            raise ValueError("At least one encryption key is required.")

    @property
    def current(self) -> EncryptionKey:
        return self.keys[0]


def decode_encryption_key(value: str, label: str) -> bytes:
    try:
        key = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError(f"{label} must be valid Base64.") from error
    if len(key) != 32 or base64.b64encode(key).decode() != value:
        raise ValueError(f"{label} must decode to exactly 32 bytes.")
    return key


def _associated_data(location: str, purpose: str, key_version: str) -> bytes:
    def part(value: str) -> str:
        return f"{len(value.encode('utf-8'))}:{value}"

    return (
        f"application-encryption|{ENVELOPE_VERSION}|{part(key_version)}|"
        f"{part(location)}|{part(purpose)}"
    ).encode()


def is_encryption_envelope(value: object) -> bool:
    return isinstance(value, dict) and set(value) == _ENVELOPE_FIELDS


def resembles_encryption_envelope(value: object) -> bool:
    return isinstance(value, dict) and bool(_ENVELOPE_FIELDS.intersection(value))


class Encryption:
    def __init__(self, keyring: EncryptionKeyring):
        versions = [entry.version for entry in keyring.keys]
        if len(versions) != len(set(versions)):
            raise ValueError("Encryption key versions must be unique.")
        self.keyring = keyring
        self._keys_by_version = {entry.version: entry for entry in keyring.keys}

    def encrypt(self, location: str, purpose: str, value: Any) -> Any:
        current = self.keyring.current
        nonce = os.urandom(12)
        encrypted = AESGCM(current.key).encrypt(
            nonce,
            json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode(),
            _associated_data(location, purpose, current.version),
        )
        return {
            "version": ENVELOPE_VERSION,
            "key-version": current.version,
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(encrypted[:-16]).decode(),
            "tag": base64.b64encode(encrypted[-16:]).decode(),
        }

    def decrypt(self, location: str, purpose: str, value: Any) -> Any:
        if not is_encryption_envelope(value):
            if resembles_encryption_envelope(value):
                raise ValueError("Malformed encryption envelope.")
            raise ValueError("Unencrypted protected value is not permitted.")
        if value["version"] != ENVELOPE_VERSION:
            raise ValueError(
                f"Unsupported encryption envelope version: {value['version']}."
            )
        key_version = value["key-version"]
        if not isinstance(key_version, str):
            raise ValueError("Malformed encryption key version.")
        entry = self._keys_by_version.get(key_version)
        if entry is None:
            raise ValueError("Unknown encryption key version.")
        try:
            nonce = base64.b64decode(value["nonce"], validate=True)
            ciphertext = base64.b64decode(value["ciphertext"], validate=True)
            tag = base64.b64decode(value["tag"], validate=True)
        except (TypeError, ValueError, binascii.Error) as error:
            raise ValueError("Malformed encryption envelope encoding.") from error
        if len(nonce) != 12 or len(tag) != 16:
            raise ValueError("Malformed encryption nonce or tag.")
        try:
            plaintext = AESGCM(entry.key).decrypt(
                nonce,
                ciphertext + tag,
                _associated_data(location, purpose, entry.version),
            )
        except InvalidTag as error:
            raise ValueError("Encryption authentication failed.") from error
        return json.loads(plaintext)


def _local_keys(environment: Mapping[str, str]) -> tuple[EncryptionKey, ...]:
    indices = sorted(
        int(match.group(1))
        for name in environment
        if (match := _LOCAL_KEY_PATTERN.fullmatch(name)) is not None
    )
    version_indices = sorted(
        int(name.removeprefix("ENCRYPTION_KEY_VERSION_"))
        for name in environment
        if name.startswith("ENCRYPTION_KEY_VERSION_")
        and name.removeprefix("ENCRYPTION_KEY_VERSION_").isdigit()
    )
    configured = sorted(set(indices) | set(version_indices))
    if not configured:
        raise ValueError("At least one local encryption key is required.")
    expected = list(range(1, configured[-1] + 1))
    if configured != expected:
        raise ValueError("Local encryption keys must use contiguous indices from 1.")
    entries: list[EncryptionKey] = []
    for index in expected:
        key_name = f"ENCRYPTION_KEY_{index}"
        version_name = f"ENCRYPTION_KEY_VERSION_{index}"
        value = environment.get(key_name)
        version = environment.get(version_name)
        if not value or not version:
            raise ValueError(f"{key_name} requires both key and version.")
        entries.append(EncryptionKey(version, decode_encryption_key(value, key_name)))
    return tuple(entries)


def load_local_encryption_keyring(
    environment: Mapping[str, str] = os.environ,
) -> EncryptionKeyring:
    return EncryptionKeyring(keys=_local_keys(environment))


def _created_at(properties: Any) -> datetime:
    created = getattr(properties, "created_on", None)
    if not isinstance(created, datetime):
        raise ValueError("Encryption secret version is missing its creation time.")
    return created


def _validate_secret_versions(ordered: list[Any]) -> None:
    created_times = [_created_at(properties) for properties in ordered]
    if len(created_times) != len(set(created_times)):
        raise ValueError("Encryption secret version order is ambiguous.")
    for properties in ordered:
        version = getattr(properties, "version", None)
        if not version:
            raise ValueError("Encryption secret metadata is missing a version.")
        if getattr(properties, "enabled", None) is False:
            raise ValueError(f"Encryption secret version {version} is disabled.")


def _load_historical_keys(
    client: Any, secret_name: str, ordered: list[Any]
) -> list[EncryptionKey]:
    loaded: list[EncryptionKey] = []
    for properties in ordered:
        version = properties.version
        secret = client.get_secret(secret_name, version)
        if not secret.value or getattr(secret.properties, "version", None) != version:
            raise ValueError(f"Encryption secret version {version} is incomplete.")
        loaded.append(
            EncryptionKey(
                version,
                decode_encryption_key(secret.value, f"{secret_name} {version}"),
            )
        )
    return loaded


def load_key_vault_encryption_keyring(client: Any) -> EncryptionKeyring:
    """Load every secret version once, ordered newest to oldest."""
    secret_name = "application-encryption-key"
    for _ in range(3):
        first_latest = client.get_secret(secret_name)
        first_version = getattr(first_latest.properties, "version", None)
        if not first_latest.value or not first_version:
            raise ValueError("Current encryption secret is incomplete.")

        versions = list(client.list_properties_of_secret_versions(secret_name))
        ordered = sorted(versions, key=_created_at, reverse=True)
        if not ordered or getattr(ordered[0], "version", None) != first_version:
            continue
        _validate_secret_versions(ordered)

        loaded: list[EncryptionKey] = [
            EncryptionKey(
                first_version,
                decode_encryption_key(first_latest.value, secret_name),
            )
        ]
        loaded.extend(_load_historical_keys(client, secret_name, ordered[1:]))

        second_latest = client.get_secret(secret_name)
        if getattr(second_latest.properties, "version", None) != first_version:
            continue
        return EncryptionKeyring(keys=tuple(loaded))
    raise ValueError("Encryption secret rotated during startup discovery.")
