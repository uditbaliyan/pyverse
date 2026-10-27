from django.apps import AppConfig


class PuputAppConfig(AppConfig):
    name = "pyverse.puput"
    verbose_name = "pyverse.Puput"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        import pyverse.puput.signals  # noqa: F401, PLC0415
