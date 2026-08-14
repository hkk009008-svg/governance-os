"""Generate per-seat Ed25519 keypairs: public keys -> committed registry,
private keys -> off-repo keystore. CLI:
  python -m threeway.keys_bootstrap --registry coordination/threeway/keys \
      --keystore "$THREEWAY_KEYSTORE"
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import stat
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from threeway import keys

SEATS = (
    "director", "operator", "coordinator",
    "director2", "operator2", "coordinator2",
    "overseer", "ci", "merge-gate",
    "chief-claude", "chief-codex",
)


class BootstrapError(RuntimeError):
    """The key directories are unsafe or contain a partial roster."""


def _key_inventory(directory: Path, suffix: str) -> set[str]:
    if directory.is_symlink():
        raise BootstrapError(f"key directory must not be a symlink: {directory}")
    if not directory.exists():
        return set()
    try:
        if not directory.is_dir():
            raise BootstrapError(f"key path is not a directory: {directory}")
        return {path.name for path in directory.iterdir() if path.name.endswith(suffix)}
    except OSError as exc:
        raise BootstrapError(f"cannot inspect key directory {directory}: {exc}") from exc


def _validate_regular(path: Path, *, mode: int | None = None) -> None:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise BootstrapError(f"cannot inspect key file {path}: {exc}") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise BootstrapError(
            "partial or unsafe roster: key must be a regular non-symlink: "
            f"{path}"
        )
    if mode is not None and stat.S_IMODE(metadata.st_mode) != mode:
        raise BootstrapError(f"partial or unsafe roster: {path} must have mode {mode:04o}")


def _roster_state(registry: Path, keystore: Path, seats: tuple[str, ...]) -> str:
    expected_public = {f"{seat}.pub" for seat in seats}
    expected_private = {f"{seat}.ed25519" for seat in seats}
    actual_public = _key_inventory(registry, ".pub")
    actual_private = _key_inventory(keystore, ".ed25519")
    if not actual_public and not actual_private:
        return "empty"
    if actual_public != expected_public or actual_private != expected_private:
        raise BootstrapError(
            "partial key roster: public/private key names must exactly match the requested seats"
        )

    keys._secure_keystore_directory(keystore)
    for seat in seats:
        public_path = registry / f"{seat}.pub"
        private_path = keystore / f"{seat}.ed25519"
        _validate_regular(public_path)
        _validate_regular(private_path, mode=0o600)
        try:
            public = public_path.read_text(encoding="ascii").strip()
            private_value = private_path.read_text(encoding="ascii").strip()
            if len(private_value) != 64 or private_value.lower() != private_value:
                raise ValueError("private key is not one lowercase 32-byte seed")
            private = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(private_value))
        except (OSError, UnicodeError, ValueError, PermissionError) as exc:
            raise BootstrapError(f"partial or unsafe roster for {seat}: {exc}") from exc
        if keys.public_hex(private) != public:
            raise BootstrapError(f"partial key roster: public/private mismatch for {seat}")
    return "complete"


def _prepare_empty_directories(registry: Path, keystore: Path) -> None:
    if registry.is_symlink() or keystore.is_symlink():
        raise BootstrapError("registry and keystore directories must not be symlinks")
    registry.mkdir(parents=True, exist_ok=True)
    keystore_existed = keystore.exists()
    keystore.mkdir(parents=True, mode=0o700, exist_ok=True)
    if not keystore_existed:
        try:
            keystore.chmod(0o700)
        except OSError as exc:
            raise BootstrapError(f"cannot secure new keystore directory {keystore}: {exc}") from exc
    keys._secure_keystore_directory(keystore)


def _validate_directory_separation(registry: Path, keystore: Path) -> None:
    """Keep private material outside the public registry tree in both directions."""

    try:
        resolved_registry = registry.resolve(strict=False)
        resolved_keystore = keystore.resolve(strict=False)
    except OSError as exc:
        raise BootstrapError(f"cannot resolve key directories: {exc}") from exc
    if (
        resolved_registry == resolved_keystore
        or resolved_registry in resolved_keystore.parents
        or resolved_keystore in resolved_registry.parents
    ):
        raise BootstrapError(
            "registry and keystore must be separate, non-nested directories"
        )


CreatedFile = tuple[Path, int, int]


def _remove_created_file(created: CreatedFile) -> str | None:
    """Quarantine a pathname atomically, then delete only the created inode.

    A check followed by ``unlink(path)`` has a replacement race. Moving the
    current pathname into a private same-filesystem directory lets us inspect
    the object actually removed from the namespace. A replacement is linked
    back without overwriting any concurrent path and is never deleted.

    The created inode is pinned with a live FD before rename so a Linux
    replacement cannot reuse ``(st_dev, st_ino)`` during the quarantine.
    """

    path, device, inode = created
    pin_fd = -1
    try:
        try:
            pin_fd = os.open(
                path,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_NONBLOCK", 0)
                | getattr(os, "O_CLOEXEC", 0),
            )
        except FileNotFoundError:
            return None
        except OSError as exc:
            return f"cannot pin {path} before rollback: {exc}"
        try:
            rollback_dir = Path(
                tempfile.mkdtemp(prefix=f".{path.name}.rollback-", dir=path.parent)
            )
        except OSError as exc:
            return f"cannot create rollback quarantine beside {path}: {exc}"
        quarantine = rollback_dir / "entry"
        try:
            os.rename(path, quarantine)
        except FileNotFoundError:
            try:
                rollback_dir.rmdir()
            except OSError as exc:
                return f"{path} was already absent, but rollback cleanup failed: {exc}"
            return None
        except OSError as exc:
            try:
                rollback_dir.rmdir()
            except OSError:
                pass
            return f"cannot quarantine {path}: {exc}"

        try:
            metadata = quarantine.lstat()
        except OSError as exc:
            return f"cannot inspect quarantined entry {quarantine}: {exc}"
        created_inode = (
            metadata.st_dev == device
            and metadata.st_ino == inode
            and stat.S_ISREG(metadata.st_mode)
        )
        if created_inode:
            try:
                quarantine.unlink()
                rollback_dir.rmdir()
            except OSError as exc:
                return f"cannot remove quarantined created file {quarantine}: {exc}"
            return None

        try:
            os.link(quarantine, path, follow_symlinks=False)
        except FileExistsError:
            return (
                f"refusing to remove replaced path {path}; another path appeared and "
                f"the displaced entry is preserved at {quarantine}"
            )
        except OSError as exc:
            return (
                f"refusing to remove replaced or non-regular path {path}; could not "
                f"restore it from {quarantine}: {exc}"
            )
        try:
            quarantine.unlink()
            rollback_dir.rmdir()
        except OSError as exc:
            return f"replacement was restored at {path}, but quarantine cleanup failed: {exc}"
        return f"refusing to remove replaced path {path}; replacement was restored"
    finally:
        if pin_fd >= 0:
            os.close(pin_fd)


def _rollback_created_files(created: list[CreatedFile]) -> list[str]:
    failures: list[str] = []
    for item in reversed(created):
        failure = _remove_created_file(item)
        if failure is not None:
            failures.append(failure)
    return failures


def _write_exclusive(
    path: Path,
    value: str,
    mode: int,
    created_log: list[CreatedFile] | None = None,
) -> CreatedFile:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags, mode)
    except OSError as exc:
        raise BootstrapError(f"refusing to overwrite key path {path}: {exc}") from exc
    created: CreatedFile | None = None
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise BootstrapError(f"new key path is not a regular file: {path}")
        created = (path, metadata.st_dev, metadata.st_ino)
        with os.fdopen(descriptor, "w", encoding="ascii", closefd=True) as handle:
            descriptor = -1
            handle.write(value + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        if created_log is not None:
            created_log.append(created)
        return created
    except BaseException as exc:
        if created is not None:
            failure = _remove_created_file(created)
            if failure is not None:
                raise BootstrapError(
                    f"key write failed and rollback was incomplete: {failure}"
                ) from exc
        raise
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _validate_seats(values: list[str]) -> tuple[str, ...]:
    if not values:
        raise BootstrapError("key roster must name at least one seat")
    seats = tuple(keys.validate_seat_name(value) for value in values)
    if len(set(seats)) != len(seats):
        raise BootstrapError("key roster contains duplicate seats")
    return seats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--keystore", required=True)
    ap.add_argument("--seats", nargs="*", default=list(SEATS))
    args = ap.parse_args(argv)
    reg = Path(args.registry)
    ks = Path(args.keystore)
    created: list[CreatedFile] = []
    try:
        seats = _validate_seats(args.seats)
        _validate_directory_separation(reg, ks)
        state = _roster_state(reg, ks, seats)
        if state == "complete":
            print(f"keys already provisioned for exact roster in {reg}; no files changed")
            return 0
        _prepare_empty_directories(reg, ks)
        generated = [(seat, *keys.generate_keypair()) for seat in seats]
        for seat, private, public in generated:
            _write_exclusive(
                ks / f"{seat}.ed25519",
                keys.private_to_hex(private),
                0o600,
                created,
            )
            _write_exclusive(reg / f"{seat}.pub", public, 0o644, created)
            print(f"generated {seat}: pub -> {reg}/{seat}.pub")
        return 0
    except BaseException as exc:
        rollback_failures = _rollback_created_files(created)
        if not isinstance(exc, (BootstrapError, OSError, ValueError)):
            if rollback_failures:
                raise BootstrapError(
                    "key bootstrap was interrupted and rollback was incomplete: "
                    + "; ".join(rollback_failures)
                ) from exc
            raise
        detail = str(exc)
        if rollback_failures:
            detail += "; rollback incomplete: " + "; ".join(rollback_failures)
        print(f"keys-bootstrap: {detail}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
