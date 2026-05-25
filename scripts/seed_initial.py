"""
Script de inicialización: crea roles, estados, módulos, permisos y el primer usuario ADMIN.
Ejecutar dentro del contenedor:
    docker exec -it fastapi_app python scripts/seed_initial.py
"""

import sys
sys.path.insert(0, "/app")

from app.db.session import SessionLocal
from app.services.bootstrap_service import bootstrap_service
from app.crud.user_crud import user_crud
from app.crud.role_crud import role_crud


def main():
    db = SessionLocal()

    # 1. Ejecutar bootstrap (roles, statuses, modules, permisos)
    print("🔧 Ejecutando bootstrap...")
    result = bootstrap_service.bootstrap(db)
    print(f"   Roles creados: {result['roles_created']}")
    print(f"   Estados creados: {result['ticket_statuses_created']}")
    print(f"   Módulos creados: {result['modules_created']}")
    print(f"   Permisos creados: {result['module_roles_created']}")

    # 2. Crear usuario ADMIN si no existe
    admin_email = "admin@progestec.com"
    admin_password = "Admin123!"  # Cambiar después del primer login

    existing = user_crud.get_by_email(db, admin_email)
    if existing:
        print(f"\n✅ Usuario ADMIN ya existe: {admin_email}")
    else:
        admin_role = role_crud.get_by_name(db, "ADMIN")
        if not admin_role:
            print("❌ Error: rol ADMIN no encontrado después del bootstrap")
            db.close()
            return

        user_crud.create_user(
            db,
            email=admin_email,
            password=admin_password,
            full_name="Administrador ProGesTec",
            identification="0000000001",
            phone="3000000000",
            role_id=admin_role.id,
            identification_type="CC",
            must_change_password=False,
        )
        print(f"\n✅ Usuario ADMIN creado:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   ⚠️  Cambia la contraseña después del primer login")

    db.close()
    print("\n🚀 Base de datos lista. Ya puedes usar el sistema.")


if __name__ == "__main__":
    main()
