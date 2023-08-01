from app import db, admin
from flask import redirect, url_for
from app.models import User, EnglishClasses, Role
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.role.role == 'admin'
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('core_bp.home'))

class AdminUserView(AdminModelView):
    column_hide_backrefs = False
    column_list = ['email', 'first_name', 'last_name', 'join_date', 'last_login', 'pw_last_set', 'oauth', 'account_email_verified', 'classes_not_dynamic', 'role']
    column_searchable_list = ['email']
    form_columns = ('email', 'first_name', 'last_name', 'join_date', 'last_login', 'oauth', 'classes', 'role', 'account_email_verified')
    page_size = 50
    create_modal = True
    edit_modal = True

class AdminClassView(AdminModelView):
    column_hide_backrefs = False
    column_list = ['id', 'start_time', 'end_time', 'students_not_dynamic']
    column_searchable_list = []
    form_columns = ('id', 'start_time', 'end_time', 'students')
    page_size = 50
    create_modal = True
    edit_modal = True

class AdminRoleView(AdminModelView):
    column_hide_backrefs = False
    column_list = ['role', 'users']
    column_searchable_list = []
    form_columns = ('id', 'role', 'users')
    page_size = 50
    create_modal = True
    edit_modal = True

# admin.index_view(MyAdminIndexView, db.session)
print('ADMIN', admin)
admin.add_view(AdminUserView(User, db.session))
admin.add_view(AdminClassView(EnglishClasses, db.session))
admin.add_view(AdminRoleView(Role, db.session))