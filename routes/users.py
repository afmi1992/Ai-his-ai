from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models.user import User, Role
from auth.forms import CreateUserForm, EditUserForm


def register_user_routes(app):

    @app.route("/users")
    @login_required
    def users():
        users_list = User.query.filter_by(is_deleted=False).all()
        return render_template("users.html", users=users_list)

    @app.route("/users/create", methods=["GET", "POST"])
    @login_required
    def create_user():
        form = CreateUserForm()

        roles = Role.query.all()
        form.role_id.choices = [(role.id, role.name) for role in roles]

        if form.validate_on_submit():
            existing_user = User.query.filter_by(email=form.email.data).first()

            if existing_user:
                flash("Email already exists", "danger")
                return redirect(url_for("create_user"))

            selected_role = Role.query.get(form.role_id.data)

            new_user = User(
                full_name=form.full_name.data,
                email=form.email.data,
                role=selected_role
            )

            new_user.set_password(form.password.data)

            db.session.add(new_user)
            db.session.commit()

            flash("User created successfully", "success")
            return redirect(url_for("users"))

        return render_template("create_user.html", form=form)

    @app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_user(user_id):
        user = User.query.get_or_404(user_id)
        form = EditUserForm()

        roles = Role.query.all()
        form.role_id.choices = [(role.id, role.name) for role in roles]

        if form.validate_on_submit():
            if user.role and user.role.name == "super_admin":
                super_admin_role = Role.query.filter_by(name="super_admin").first()

                if form.role_id.data != super_admin_role.id:
                    flash("Super Admin role cannot be changed.", "danger")
                    return redirect(url_for("edit_user", user_id=user.id))
            user.full_name = form.full_name.data
            user.email = form.email.data
            user.role_id = form.role_id.data

            db.session.commit()

            flash("User updated successfully", "success")
            return redirect(url_for("users"))

        form.full_name.data = user.full_name
        form.email.data = user.email
        form.role_id.data = user.role_id

        return render_template("edit_user.html", form=form, user=user)

    @app.route("/users/<int:user_id>/delete")
    @login_required
    def delete_user(user_id):

        user = User.query.get_or_404(user_id)

        if user.role and user.role.name == "super_admin":
            flash("Super Admin account cannot be deleted.", "danger")
            return redirect(url_for("users"))

        user.is_deleted = True
        db.session.commit()

        flash("User deleted successfully", "success")
        return redirect(url_for("users"))