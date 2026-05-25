# app/core/roles.py

from app.models.user import User

# Códigos de roles
ROLE_ADMIN = "ADMIN"
ROLE_ADVISOR = "ADVISOR"
ROLE_TECHNICIAN = "TECHNICIAN"
ROLE_CLIENT = "CLIENT"
ROLE_COURIER = "COURIER"

# Agrupaciones útiles
TICKET_CREATORS = (ROLE_ADMIN, ROLE_ADVISOR)
DEVICE_CREATORS = (ROLE_ADMIN, ROLE_ADVISOR)


def get_role_name(user: User) -> str | None:
    return user.role.name if user.role else None


def user_has_role(user: User, *roles: str) -> bool:
    role_name = get_role_name(user)
    return role_name in roles
