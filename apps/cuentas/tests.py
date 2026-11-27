from unittest.mock import Mock, patch

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import UserManager
from django.core.exceptions import PermissionDenied
from django.db import models
from django.test import RequestFactory, SimpleTestCase

from .admin import UsuarioAdmin
from .models import Usuario, UsuarioManager

PERMISOS_ADMIN_NORMAL = {
    "cuentas.add_usuario",
    "cuentas.change_usuario",
    "cuentas.view_usuario",
}


def _usuario(
    pk,
    is_superuser=False,
    is_staff=True,
    is_active=True,
    permisos=PERMISOS_ADMIN_NORMAL,
):
    usuario = Mock(
        pk=pk,
        rol=Usuario.Rol.ADMINISTRADOR,
        is_superuser=is_superuser,
        is_staff=is_staff,
        is_active=is_active,
        is_authenticated=True,
    )
    if is_superuser:
        usuario.has_perm = Mock(return_value=True)
    else:
        usuario.has_perm = Mock(side_effect=lambda codename: codename in permisos)
    return usuario


def _objetivo(pk, rol=Usuario.Rol.USUARIO, is_superuser=False):
    return Mock(pk=pk, rol=rol, is_superuser=is_superuser)


class UsuarioModeloTests(SimpleTestCase):
    """Pruebas del modelo que no requieren base de datos."""

    def test_rol_por_defecto_es_usuario(self):
        self.assertEqual(Usuario(username="prueba").rol, Usuario.Rol.USUARIO)

    def test_roles_disponibles(self):
        self.assertEqual(
            list(Usuario.Rol.choices),
            [("administrador", "Administrador"), ("usuario", "Usuario")],
        )

    def test_es_administrador_por_rol(self):
        usuario = Usuario(username="prueba", rol=Usuario.Rol.ADMINISTRADOR)
        self.assertTrue(usuario.es_administrador)

    def test_es_administrador_falso_para_usuario(self):
        usuario = Usuario(username="prueba", rol=Usuario.Rol.USUARIO)
        self.assertFalse(usuario.es_administrador)

    def test_es_administrador_para_superusuario(self):
        usuario = Usuario(
            username="prueba",
            rol=Usuario.Rol.USUARIO,
            is_superuser=True,
        )
        self.assertTrue(usuario.es_administrador)

    def test_manager_personalizado(self):
        self.assertIsInstance(Usuario.objects, UsuarioManager)

    def test_restricciones_de_rol(self):
        nombres = {restriccion.name for restriccion in Usuario._meta.constraints}
        self.assertIn("cuentas_usuario_rol_valido", nombres)
        self.assertIn("cuentas_usuario_superusuario_administrador", nombres)

    def test_str_usa_nombre_completo(self):
        usuario = Usuario(username="prueba", first_name="Ana", last_name="Pérez")
        self.assertEqual(str(usuario), "Ana Pérez")

    def test_str_usa_username_sin_nombre(self):
        self.assertEqual(str(Usuario(username="prueba")), "prueba")

    def test_save_fuerza_rol_de_superusuario(self):
        usuario = Usuario(
            username="prueba",
            rol=Usuario.Rol.USUARIO,
            is_superuser=True,
        )
        with patch.object(models.Model, "save") as guardar:
            usuario.save()
        self.assertEqual(usuario.rol, Usuario.Rol.ADMINISTRADOR)
        guardar.assert_called_once()

    def test_save_respeta_rol_de_usuario_normal(self):
        usuario = Usuario(username="prueba", rol=Usuario.Rol.USUARIO)
        with patch.object(models.Model, "save"):
            usuario.save()
        self.assertEqual(usuario.rol, Usuario.Rol.USUARIO)

    def test_save_anade_rol_a_update_fields(self):
        usuario = Usuario(
            username="prueba",
            rol=Usuario.Rol.USUARIO,
            is_superuser=True,
        )
        with patch.object(models.Model, "save") as guardar:
            usuario.save(update_fields=["last_login"])
        _, kwargs = guardar.call_args
        self.assertEqual(set(kwargs["update_fields"]), {"last_login", "rol"})

    def test_create_superuser_asigna_rol(self):
        with patch.object(
            UserManager,
            "create_superuser",
            return_value="creado",
        ) as crear:
            resultado = Usuario.objects.create_superuser(
                "prueba",
                "prueba@example.com",
                "clave",
            )
        self.assertEqual(resultado, "creado")
        self.assertEqual(
            crear.call_args.kwargs.get("rol"),
            Usuario.Rol.ADMINISTRADOR,
        )


class UsuarioAdminTests(SimpleTestCase):
    """Pruebas de autorización del admin sin base de datos."""

    def setUp(self):
        self.model_admin = UsuarioAdmin(Usuario, admin.site)
        self.factory = RequestFactory()
        self.superuser = _usuario(1, is_superuser=True)
        self.admin = _usuario(2)
        self.otro_admin = _objetivo(4, rol=Usuario.Rol.ADMINISTRADOR)
        self.usuario_normal = _objetivo(3)

    def _request(self, usuario):
        request = self.factory.get("/admin/")
        request.user = usuario
        return request

    def _campos(self, fieldsets):
        return [
            campo
            for _, opciones in fieldsets
            for campo in opciones.get("fields", ())
        ]

    # --- fieldsets y formularios ---

    def test_no_superusuario_no_ve_campos_reservados(self):
        fieldsets = self.model_admin.get_fieldsets(
            self._request(self.admin),
            obj=Usuario(username="prueba"),
        )
        campos = self._campos(fieldsets)
        for campo in UsuarioAdmin.CAMPOS_RESERVADOS_A_SUPERUSUARIO:
            self.assertNotIn(campo, campos)

    def test_no_superusuario_no_ve_rol_al_crear(self):
        fieldsets = self.model_admin.get_fieldsets(self._request(self.admin), obj=None)
        self.assertNotIn("rol", self._campos(fieldsets))

    def test_superusuario_ve_campos_reservados(self):
        fieldsets = self.model_admin.get_fieldsets(
            self._request(self.superuser),
            obj=Usuario(username="prueba"),
        )
        campos = self._campos(fieldsets)
        for campo in UsuarioAdmin.CAMPOS_RESERVADOS_A_SUPERUSUARIO:
            self.assertIn(campo, campos)

    def test_formulario_edicion_admin_normal_usa_lista_blanca(self):
        formulario = self.model_admin.get_form(
            self._request(self.admin),
            obj=self.usuario_normal,
        )
        campos = set(formulario.base_fields)
        self.assertEqual(
            campos,
            set(UsuarioAdmin.CAMPOS_PERMITIDOS_EDICION_ADMIN_NORMAL),
        )

    def test_formulario_alta_admin_normal_no_permite_rol_ni_privilegios(self):
        formulario = self.model_admin.get_form(self._request(self.admin), obj=None)
        campos = set(formulario.base_fields)
        self.assertEqual(
            campos,
            set(UsuarioAdmin.CAMPOS_PERMITIDOS_ALTA_ADMIN_NORMAL),
        )

    def test_formulario_alta_superusuario_incluye_rol(self):
        formulario = self.model_admin.get_form(self._request(self.superuser), obj=None)
        campos = set(formulario.base_fields)
        self.assertIn("rol", campos)
        self.assertNotIn("is_staff", campos)
        self.assertNotIn("groups", campos)

    def test_formulario_edicion_superusuario_incluye_todos(self):
        formulario = self.model_admin.get_form(
            self._request(self.superuser),
            obj=self.otro_admin,
        )
        campos = set(formulario.base_fields)
        for campo in UsuarioAdmin.CAMPOS_RESERVADOS_A_SUPERUSUARIO:
            self.assertIn(campo, campos)

    def test_fechas_solo_lectura_para_admin_normal(self):
        readonly = self.model_admin.get_readonly_fields(
            self._request(self.admin),
            obj=self.usuario_normal,
        )
        for campo in UsuarioAdmin.CAMPOS_SOLO_LECTURA_ADMIN_NORMAL:
            self.assertIn(campo, readonly)

    def test_fechas_no_son_solo_lectura_para_superusuario(self):
        readonly = self.model_admin.get_readonly_fields(
            self._request(self.superuser),
            obj=self.usuario_normal,
        )
        for campo in UsuarioAdmin.CAMPOS_SOLO_LECTURA_ADMIN_NORMAL:
            self.assertNotIn(campo, readonly)

    # --- consulta y visibilidad ---

    def test_get_queryset_admin_normal_excluye_otros_administradores(self):
        qs = Mock()
        qs.order_by.return_value = qs
        qs.filter.return_value = qs
        with patch.object(Usuario._default_manager, "get_queryset", return_value=qs):
            self.model_admin.get_queryset(self._request(self.admin))
        qs.filter.assert_called_once()
        condicion = str(qs.filter.call_args.args[0])
        self.assertIn("is_superuser", condicion)
        self.assertIn("rol", condicion)

    def test_get_queryset_superusuario_no_filtra(self):
        qs = Mock()
        qs.order_by.return_value = qs
        qs.filter.return_value = qs
        with patch.object(Usuario._default_manager, "get_queryset", return_value=qs):
            self.model_admin.get_queryset(self._request(self.superuser))
        qs.filter.assert_not_called()

    # --- permisos ---

    def test_no_superusuario_no_puede_ver_otro_administrador(self):
        request = self._request(self.admin)
        self.assertFalse(
            self.model_admin.has_view_permission(request, self.otro_admin)
        )

    def test_no_superusuario_puede_ver_usuario_normal(self):
        request = self._request(self.admin)
        self.assertTrue(
            self.model_admin.has_view_permission(request, self.usuario_normal)
        )

    def test_no_superusuario_no_puede_cambiar_superusuario(self):
        objetivo = Mock(pk=5, rol=Usuario.Rol.ADMINISTRADOR, is_superuser=True)
        self.assertFalse(
            self.model_admin.has_change_permission(self._request(self.admin), objetivo)
        )

    def test_no_superusuario_no_puede_cambiar_otro_administrador(self):
        self.assertFalse(
            self.model_admin.has_change_permission(
                self._request(self.admin),
                self.otro_admin,
            )
        )

    def test_no_superusuario_puede_cambiar_usuario_normal(self):
        self.assertTrue(
            self.model_admin.has_change_permission(
                self._request(self.admin),
                self.usuario_normal,
            )
        )

    def test_no_superusuario_puede_cambiar_propia_cuenta(self):
        self.assertTrue(
            self.model_admin.has_change_permission(self._request(self.admin), self.admin)
        )

    def test_no_superusuario_no_puede_borrar_usuarios(self):
        con_permiso = _usuario(
            6,
            permisos=PERMISOS_ADMIN_NORMAL | {"cuentas.delete_usuario"},
        )
        request = self._request(con_permiso)
        self.assertFalse(self.model_admin.has_delete_permission(request))
        self.assertFalse(
            self.model_admin.has_delete_permission(request, self.usuario_normal)
        )

    def test_no_superusuario_no_tiene_accion_borrar_seleccionados(self):
        acciones = self.model_admin.get_actions(self._request(self.admin))
        self.assertNotIn("delete_selected", acciones)

    def test_superusuario_puede_cambiar_y_borrar_otro_administrador(self):
        request = self._request(self.superuser)
        self.assertTrue(
            self.model_admin.has_change_permission(request, self.otro_admin)
        )
        self.assertTrue(
            self.model_admin.has_delete_permission(request, self.otro_admin)
        )

    def test_superusuario_puede_crear_usuarios(self):
        self.assertTrue(
            self.model_admin.has_add_permission(self._request(self.superuser))
        )

    def test_admin_normal_puede_crear_usuarios(self):
        self.assertTrue(
            self.model_admin.has_add_permission(self._request(self.admin))
        )

    # --- contraseñas ---

    def test_admin_normal_no_puede_cambiar_contrasena_de_otro_admin(self):
        request = self._request(self.admin)
        with patch.object(
            self.model_admin, "get_object", return_value=self.otro_admin
        ), patch.object(
            BaseUserAdmin,
            "user_change_password",
            return_value="ok",
        ) as delegar:
            with self.assertRaises(PermissionDenied):
                self.model_admin.user_change_password(request, "4")
        delegar.assert_not_called()

    def test_admin_normal_puede_cambiar_su_propia_contrasena(self):
        request = self._request(self.admin)
        with patch.object(self.model_admin, "get_object", return_value=self.admin), patch.object(
            BaseUserAdmin,
            "user_change_password",
            return_value="ok",
        ) as delegar:
            resultado = self.model_admin.user_change_password(request, "2")
        self.assertEqual(resultado, "ok")
        delegar.assert_called_once()

    def test_admin_normal_puede_cambiar_contrasena_de_usuario_normal(self):
        request = self._request(self.admin)
        with patch.object(
            self.model_admin, "get_object", return_value=self.usuario_normal
        ), patch.object(
            BaseUserAdmin,
            "user_change_password",
            return_value="ok",
        ) as delegar:
            resultado = self.model_admin.user_change_password(request, "3")
        self.assertEqual(resultado, "ok")
        delegar.assert_called_once()

    def test_user_change_password_de_superusuario_delega(self):
        request = self._request(self.superuser)
        with patch.object(self.model_admin, "get_object") as buscar, patch.object(
            BaseUserAdmin,
            "user_change_password",
            return_value="ok",
        ) as delegar:
            resultado = self.model_admin.user_change_password(request, "4")
        self.assertEqual(resultado, "ok")
        buscar.assert_not_called()
        delegar.assert_called_once()

    # --- guardado ---

    def test_save_model_admin_normal_fuerza_valores_en_alta(self):
        obj = Mock(pk=9, rol=Usuario.Rol.ADMINISTRADOR, is_staff=True, is_superuser=True)
        with patch.object(BaseUserAdmin, "save_model") as guardar:
            self.model_admin.save_model(
                self._request(self.admin),
                obj,
                Mock(),
                False,
            )
        self.assertEqual(obj.rol, Usuario.Rol.USUARIO)
        self.assertFalse(obj.is_staff)
        self.assertFalse(obj.is_superuser)
        guardar.assert_called_once()

    def test_save_model_admin_normal_no_puede_editar_otro_admin(self):
        with patch.object(BaseUserAdmin, "save_model") as guardar:
            with self.assertRaises(PermissionDenied):
                self.model_admin.save_model(
                    self._request(self.admin),
                    self.otro_admin,
                    Mock(),
                    True,
                )
        guardar.assert_not_called()

    def test_save_model_admin_normal_no_puede_convertir_usuario_en_admin(self):
        obj = Mock(pk=3, rol=Usuario.Rol.USUARIO, is_staff=True, is_superuser=False)
        with patch.object(BaseUserAdmin, "save_model") as guardar:
            self.model_admin.save_model(
                self._request(self.admin),
                obj,
                Mock(),
                True,
            )
        self.assertEqual(obj.rol, Usuario.Rol.USUARIO)
        self.assertFalse(obj.is_staff)
        self.assertFalse(obj.is_superuser)
        guardar.assert_called_once()

    def test_save_model_admin_normal_puede_editar_propia_cuenta(self):
        with patch.object(BaseUserAdmin, "save_model") as guardar:
            self.model_admin.save_model(
                self._request(self.admin),
                self.admin,
                Mock(),
                True,
            )
        guardar.assert_called_once()

    # --- protección contra auto-desactivación ---

    def test_save_model_admin_normal_no_puede_desactivar_propia_cuenta(self):
        objetivo = _usuario(2)
        objetivo.is_active = False
        with patch.object(BaseUserAdmin, "save_model") as guardar:
            with self.assertRaises(PermissionDenied):
                self.model_admin.save_model(
                    self._request(self.admin),
                    objetivo,
                    Mock(),
                    True,
                )
        guardar.assert_not_called()

    def test_barrera_save_model_no_depende_del_formulario(self):
        objetivo = _usuario(2)
        objetivo.is_active = False
        formulario = Mock()
        formulario.cleaned_data = {"is_active": True}
        with patch.object(BaseUserAdmin, "save_model") as guardar:
            with self.assertRaises(PermissionDenied):
                self.model_admin.save_model(
                    self._request(self.admin),
                    objetivo,
                    formulario,
                    True,
                )
        guardar.assert_not_called()

    def test_is_active_solo_lectura_en_propia_cuenta(self):
        request = self._request(self.admin)
        readonly = self.model_admin.get_readonly_fields(request, self.admin)
        self.assertIn("is_active", readonly)
        formulario = self.model_admin.get_form(request, obj=self.admin)
        self.assertNotIn("is_active", formulario.base_fields)

    def test_admin_normal_puede_cambiar_contrasena_propia_tras_proteccion(self):
        request = self._request(self.admin)
        with patch.object(
            self.model_admin, "get_object", return_value=self.admin
        ), patch.object(
            BaseUserAdmin,
            "user_change_password",
            return_value="ok",
        ) as delegar, patch.object(
            BaseUserAdmin,
            "save_model",
        ) as guardar:
            resultado = self.model_admin.user_change_password(request, "2")
        self.assertEqual(resultado, "ok")
        delegar.assert_called_once()
        guardar.assert_not_called()

    def test_admin_normal_puede_desactivar_usuario_normal(self):
        objetivo = _objetivo(3)
        objetivo.is_active = False
        with patch.object(BaseUserAdmin, "save_model") as guardar:
            self.model_admin.save_model(
                self._request(self.admin),
                objetivo,
                Mock(),
                True,
            )
        guardar.assert_called_once()
        self.assertFalse(objetivo.is_active)

    def test_superusuario_conserva_auto_desactivacion(self):
        request = self._request(self.superuser)
        readonly = self.model_admin.get_readonly_fields(request, self.superuser)
        self.assertNotIn("is_active", readonly)
        objetivo = self.superuser
        objetivo.is_active = False
        with patch.object(BaseUserAdmin, "save_model") as guardar:
            self.model_admin.save_model(request, objetivo, Mock(), True)
        guardar.assert_called_once()

    def test_save_related_admin_normal_limpia_grupos_y_permisos_en_alta(self):
        instancia = Mock()
        instancia.groups = Mock()
        instancia.user_permissions = Mock()
        formulario = Mock(instance=instancia)
        with patch.object(BaseUserAdmin, "save_related") as guardar:
            self.model_admin.save_related(
                self._request(self.admin),
                formulario,
                [],
                False,
            )
        instancia.groups.clear.assert_called_once()
        instancia.user_permissions.clear.assert_called_once()
        guardar.assert_called_once()

    # --- acceso al panel ---

    def test_usuario_normal_no_accede_al_panel(self):
        request = self.factory.get("/admin/")
        request.user = _usuario(7, is_staff=False)
        self.assertFalse(admin.site.has_permission(request))

        request.user = _usuario(7, is_staff=True, is_active=False)
        self.assertFalse(admin.site.has_permission(request))

    def test_admin_normal_accede_al_panel(self):
        request = self.factory.get("/admin/")
        request.user = self.admin
        self.assertTrue(admin.site.has_permission(request))
