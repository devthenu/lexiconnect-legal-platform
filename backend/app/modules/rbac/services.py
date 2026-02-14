from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.modules.rbac.models import Privilege, Role, RolePrivilege, UserPrivilegeOverride, UserRole


def _get_cache(db: Session) -> dict:
    return db.info.setdefault("rbac_cache", {})


def _normalize_user_role_name(raw_role) -> str | None:
    if raw_role is None:
        return None

    if hasattr(raw_role, "name"):
        name = str(raw_role.name)
    else:
        name = str(raw_role)

    if "." in name:
        name = name.split(".")[-1]

    name = name.strip().upper()
    if not name:
        return None

    # Backward compatibility: apprentice users can map to the existing CLERK system role.
    if name == "APPRENTICE":
        return "CLERK"
    return name


def _fallback_role_id_from_user_column(db: Session, user_id: int) -> int | None:
    raw_role = db.execute(select(User.role).where(User.id == user_id)).scalar_one_or_none()
    normalized = _normalize_user_role_name(raw_role)
    if not normalized:
        return None

    return db.execute(
        select(Role.id).where(func.lower(Role.name) == normalized.lower())
    ).scalar_one_or_none()


def get_user_roles(db: Session, user_id: int) -> list[str]:
    cache = _get_cache(db)
    cache_key = f"user_roles:{user_id}"
    if cache_key in cache:
        return cache[cache_key]

    stmt = (
        select(UserRole.role_id)
        .where(UserRole.user_id == user_id)
    )
    role_ids = [row[0] for row in db.execute(stmt).all()]

    fallback_role_id = _fallback_role_id_from_user_column(db, user_id)
    if fallback_role_id and fallback_role_id not in role_ids:
        role_ids.append(fallback_role_id)

    cache[cache_key] = role_ids
    return role_ids


def get_user_effective_privilege_keys(db: Session, user_id: int) -> set[str]:
    cache = _get_cache(db)
    cache_key = f"user_privileges:{user_id}"
    if cache_key in cache:
        return cache[cache_key]

    role_ids = get_user_roles(db, user_id)
    privilege_keys: set[str] = set()

    if role_ids:
        stmt = (
            select(Privilege.key)
            .select_from(RolePrivilege)
            .join(Privilege, Privilege.id == RolePrivilege.privilege_id)
            .where(RolePrivilege.role_id.in_(role_ids))
        )
        privilege_keys.update(row[0] for row in db.execute(stmt).all())

    overrides_stmt = (
        select(UserPrivilegeOverride.effect, Privilege.key)
        .select_from(UserPrivilegeOverride)
        .join(Privilege, Privilege.id == UserPrivilegeOverride.privilege_id)
        .where(UserPrivilegeOverride.user_id == user_id)
    )
    for effect, key in db.execute(overrides_stmt).all():
        if str(effect) == "grant":
            privilege_keys.add(key)
        else:
            privilege_keys.discard(key)

    cache[cache_key] = privilege_keys
    return privilege_keys


def user_has_privilege(db: Session, user_id: int, key: str) -> bool:
    return key in get_user_effective_privilege_keys(db, user_id)
