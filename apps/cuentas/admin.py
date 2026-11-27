from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Administración interna del usuario y su rol.

    Un administrador que no sea superusuario puede gestionar únicamente
    usuarios normales (y su propia cuenta). Los campos y las cuentas
    administrativas quedan fuera de su alcance tanto en la interfaz como en
    las comprobaciones del servidor.
    """

    CAMPOS_RESERVADOS_A_SUPERUSUARIO = (
        "rol",
        "is_staff",
        "is_superuser",
        "groups",
        "user_permissions",
    )
    CAMPOS_PERMITIDOS_ALTA_ADMIN_NORMAL = (
        "username",
        "usable_password",
        "password1",
        "password2",
    )
    CAMPOS_PERMITIDOS_EDICION_ADMIN_NORMAL = (
        "username",
        "password",
        "first_name",
        "last_name",
        "email",
        "is_active",
    )
    CAMPOS_SOLO_LECTURA_ADMIN_NORMAL = ("last_login", "date_joined")

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "rol",
        "is_staff",
        "is_active",
    )
    list_filter = BaseUserAdmin.list_filter + ("rol",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Rol en SismoDetect", {"fields": ("rol",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Rol en SismoDetect", {"fields": ("rol",)}),
    )

    @staticmethod
    def _es_administrador(usuario):
        if usuario is None:
            return False
        return bool(
            getattr(usuario, "is_superuser", False)
            or getattr(usuario, "rol", None) == Usuario.Rol.ADMINISTRADOR
        )

    @classmethod
    def _es_otro_administrador(cls, usuario_actual, objetivo):
        if not getattr(usuario_actual, "is_authenticated", True):
            return True
        if not cls._es_administrador(objetivo):
            return False
        return getattr(objetivo, "pk", None) != getattr(usuario_actual, "pk", None)

    @staticmethod
    def _es_propia_cuenta(usuario_actual, objetivo):
        if objetivo is None or not getattr(usuario_actual, "is_authenticated", True):
            return False
        pk_actual = getattr(usuario_actual, "pk", None)
        return pk_actual is not None and getattr(objetivo, "pk", None) == pk_actual

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # El propio administrador debe seguir visible para poder cambiar su
        # contraseña. El resto de administradores y todos los superusuarios
        # quedan fuera de su consulta.
        return qs.filter(
            Q(pk=getattr(request.user, "pk", None))
            | (Q(is_superuser=False) & ~Q(rol=Usuario.Rol.ADMINISTRADOR))
        )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return fieldsets
        permitidos = (
            self.CAMPOS_PERMITIDOS_ALTA_ADMIN_NORMAL
            if obj is None
            else self.CAMPOS_PERMITIDOS_EDICION_ADMIN_NORMAL
        )
        return self._solo_campos_permitidos(fieldsets, permitidos)

    def _solo_campos_permitidos(self, fieldsets, permitidos):
        resultado = []
        for nombre, opciones in fieldsets:
            campos = [
                campo
                for campo in opciones.get("fields", ())
                if campo in permitidos
            ]
            if campos:
                opciones_filtradas = dict(opciones)
                opciones_filtradas["fields"] = campos
                resultado.append((nombre, opciones_filtradas))
        return resultado

    def get_form(self, request, obj=None, **kwargs):
        # Lista blanca: incluso si llega un ``fields`` externo o un POST con
        # claves adicionales, el formulario solo puede contener estos campos.
        if not request.user.is_superuser:
            permitidos = (
                self.CAMPOS_PERMITIDOS_ALTA_ADMIN_NORMAL
                if obj is None
                else self.CAMPOS_PERMITIDOS_EDICION_ADMIN_NORMAL
            )
            readonly = self.get_readonly_fields(request, obj)
            kwargs["fields"] = [
                campo for campo in permitidos if campo not in readonly
            ]
        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly = tuple(super().get_readonly_fields(request, obj))
        if request.user.is_superuser:
            return readonly
        readonly += self.CAMPOS_SOLO_LECTURA_ADMIN_NORMAL
        # La propia cuenta no puede desactivarse desde el formulario. Esta
        # medida es complementaria; la barrera definitiva esta en save_model().
        if self._es_propia_cuenta(request.user, obj):
            readonly += ("is_active",)
        return readonly

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            actions.pop("delete_selected", None)
        return actions

    def has_view_permission(self, request, obj=None):
        if (
            not request.user.is_superuser
            and obj is not None
            and self._es_otro_administrador(request.user, obj)
        ):
            return False
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if (
            not request.user.is_superuser
            and obj is not None
            and self._es_otro_administrador(request.user, obj)
        ):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def user_change_password(self, request, id, form_url=""):
        # Barrera adicional antes de delegar en UserAdmin: la URL directa de
        # cambio de contraseña no permite afectar a otro administrador.
        if not request.user.is_superuser:
            objetivo = self.get_object(request, unquote(id))
            if objetivo is None:
                raise Http404("El usuario no existe.")
            if self._es_otro_administrador(request.user, objetivo):
                raise PermissionDenied
        return super().user_change_password(request, id, form_url)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            if change and self._es_otro_administrador(request.user, obj):
                raise PermissionDenied
            # Barrera de servidor: aunque un POST manipulado consiguiera un
            # objeto con is_active=False, la propia cuenta no se desactiva.
            if (
                change
                and self._es_propia_cuenta(request.user, obj)
                and not getattr(obj, "is_active", True)
            ):
                raise PermissionDenied(
                    "Un administrador normal no puede desactivar su propia cuenta."
                )
            if not change or not self._es_administrador(obj):
                # Alta, o edición de un usuario normal: nunca puede convertirse
                # en administrador ni en miembro del staff.
                obj.rol = Usuario.Rol.USUARIO
                obj.is_staff = False
                obj.is_superuser = False
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        if not request.user.is_superuser and not change:
            instance = form.instance
            instance.groups.clear()
            instance.user_permissions.clear()
        super().save_related(request, form, formsets, change)
