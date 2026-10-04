SECRET_KEY = "test-only"
INSTALLED_APPS = ["django.contrib.contenttypes", "persian_kit"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
USE_TZ = True
USE_I18N = True
TIME_ZONE = "Asia/Tehran"
LANGUAGE_CODE = "en"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    }
]
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
