from app import create_app
from extensions import db
from models.user import User, Role

app = create_app()

with app.app_context():

    admin = User.query.filter_by(email="admin@ihis.com").first()
    super_admin_role = Role.query.filter_by(name="super_admin").first()

    if not super_admin_role:
        super_admin_role = Role(name="super_admin")
        db.session.add(super_admin_role)
        db.session.commit()

    if not admin:
        admin = User(
            full_name="System Super Admin",
            email="admin@ihis.com",
            role=super_admin_role,
            is_active_user=True
        )
        db.session.add(admin)

    admin.set_password("Admin@12345")
    admin.role = super_admin_role
    admin.is_active_user = True

    db.session.commit()

    print("Admin reset done")
    print("Password check:", admin.check_password("Admin@12345"))