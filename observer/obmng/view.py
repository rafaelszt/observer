import re
import os
import os.path as op
import uuid

from flask import g, url_for, request, abort, redirect
from flask_admin import form, expose
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib import sqla
from flask_security import current_user, utils
from werkzeug.security import generate_password_hash
from wtforms.fields import PasswordField
from jinja2 import Markup
from flask_security import login_required
from flask_mail import Message

from observer.processing.system_mng import SystemMng
from observer import app


class AdminModelView(sqla.ModelView):
    column_exclude_list = ('password')
    form_excluded_columns = ('password', 'last_login_at', 'current_login_at', 'last_login_ip',
                            'current_login_ip', 'login_count', 'confirmed_at')
    create_modal = True
    
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    # Automatically display human-readable names for the current and available Roles when creating or editing a User
    # column_auto_select_related = True
    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(AdminModelView, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

    # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
    # committed to the database.
    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):

            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            model.password = utils.encrypt_password(model.password2)


file_path = op.join(op.dirname(__file__), './static/faces')
class FaceModelView(sqla.ModelView):
    column_exclude_list = ('embedding')
    form_excluded_columns = ('embedding')
    can_edit = False

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup('<img src="%s">' % url_for('static',
                        filename=form.thumbgen_filename(op.join('faces', model.path))))

    def safe_name(obj, file_data):
        ext = file_data.filename.split('.')[-1]
        return str(uuid.uuid4()) + '.' + ext 

    def on_model_change(self, form, model, is_created):
        system_mng = SystemMng()
        model.embedding = system_mng.generate_embedding(op.join(file_path, model.path))

    def after_model_change(self, form, model, is_created):
        system_mng = SystemMng()
        system_mng.add_face(model.id, model.embedding)

    def after_model_delete(self, model):
        system_mng = SystemMng()
        system_mng.delete_face(model.id)

    column_formatters = {
        'path': _list_thumbnail
    }
    form_extra_fields = {
        'path': form.ImageUploadField('Face',
                                      base_path=file_path,
                                      thumbnail_size=(100, 100, True),
                                      namegen=safe_name)
    }


class DashboardModelView(sqla.ModelView):
    can_delete = False
    can_create = False
    can_edit = False

    def _list_thumbnail(view, context, model, name):
        if not model.image_path:
            return ''
        return Markup('<img src="%s" height="100" width="100">' % url_for('static',
                        filename=model.image_path))

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

    column_formatters = {
        'image_path': _list_thumbnail
    }


class HomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    def is_accessible(self):
        if current_user.is_active and current_user.is_authenticated:
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


from flask_admin.model import BaseModelView
from flask_admin.model.form import create_editable_list_form
from wtforms import Form, StringField
class MyForm(Form):
    name = StringField('Name')

class OptionsView(ModelView):
    can_create = False
    can_delete = False
    list_template = 'admin/empty.html'

    def is_accessible(self):
        if current_user.is_active and current_user.is_authenticated:
            return True
        return False

    # Forcing EditView of a single Item, POG I know..
    @expose('/', methods=('GET', 'POST'))
    def edit_view(self):
        """
            Edit model view
        """
        return_url = '/option/'

        if not self.can_edit:
            return redirect(return_url)

        id = '1'
        model = self.get_one(id)

        form = self.edit_form(obj=model)
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_edit_rules, form=form)

        if self.validate_form(form):
            if self.update_model(form, model):
                from flask import flash
                from flask_admin.babel import gettext
                flash(gettext('Record was successfully saved.'), 'success')
                if '_add_another' in request.form:
                    return redirect(self.get_url('.create_view', url=return_url))
                elif '_continue_editing' in request.form:
                    return redirect(request.url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=False))

        if request.method == 'GET' or form.errors:
            self.on_form_prefill(form, id)

        from flask_admin.form import FormOpts
        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        if self.edit_modal and request.args.get('modal'):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)

    def after_model_change(self, form, model, is_created):
        system_mng = SystemMng()
        system_mng.restart_cameras()