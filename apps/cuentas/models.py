from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q


class UsuarioManager(UserManager):
    """Manager que mantiene coherente el rol de los superusuarios."""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("rol", self.model.Rol.ADMINISTRADOR)
        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    """Usuario local de SismoDetect.

    Se extiende ``AbstractUser`` para conservar la autenticación estándar de
    Django y añadir el rol funcional que utilizará la interfaz.
    """

    class Rol(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        USUARIO = "usuario", "Usuario"

    rol = models.CharField(
        "rol",
        max_length=20,
        choices=Rol.choices,
        default=Rol.USUARIO,
        help_text="Rol funcional dentro de SismoDetect.",
    )

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
        constraints = (
            # Los valores válidos deben coincidir con Usuario.Rol.choices.
            models.CheckConstraint(
                condition=Q(rol__in=["administrador", "usuario"]),
                name="cuentas_usuario_rol_valido",
            ),
            # Ningún superusuario puede quedar con un rol funcional distinto.
            models.CheckConstraint(
                condition=Q(is_superuser=False) | Q(rol="administrador"),
                name="cuentas_usuario_superusuario_administrador",
            ),
        )

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.rol = self.Rol.ADMINISTRADOR
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"rol"}
        super().save(*args, **kwargs)

    @property
    def es_administrador(self) -> bool:
        return self.is_superuser or self.rol == self.Rol.ADMINISTRADOR
