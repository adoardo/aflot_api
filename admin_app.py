from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Mount, Route
from starlette_admin.contrib.mongoengine import Admin, ModelView
from mongoengine import connect, disconnect
from dotenv import load_dotenv
from af_admin.models.admin_models import (Auth, CompanyModel, CompanyTariffs, UserModel, Vacancy, NewsModel,
                                 Contact, RealHistory, SwimsTariffs, DescriptionTariffs, Navy, SettingsGlobal)
import os

from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from af_admin.admin_provider import MyAuthProvider

#ED TRANSLATE
from typing import Any, Dict, List, Optional, Tuple, Union
from starlette.types import ASGIApp, Receive, Scope, Send
import datetime
import pathlib
from dataclasses import dataclass
from contextvars import ContextVar
from babel import Locale, dates
from babel.support import LazyProxy, NullTranslations, Translations
#END ED TRANSLATE

load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
SECRET = os.getenv("SECRET_KEY")

#ED TRANSLATE
DEFAULT_LOCALE = "ru"
SUPPORTED_LOCALES = [
    "en",  # English
    "ru",  # Russian
]

translations: Dict[str, NullTranslations] = {
        locale: Translations.load(
            dirname=pathlib.Path(__file__).parent.joinpath("translations/"),
            locales=[locale],
            domain="admin",
        )
        for locale in SUPPORTED_LOCALES
    }

_current_locale: ContextVar[str] = ContextVar(
    "current_locale", default=DEFAULT_LOCALE
)
_current_translation: ContextVar[NullTranslations] = ContextVar(
    "current_translation", default=translations[DEFAULT_LOCALE]
)

def set_locale(locale: str) -> None:
    _current_locale.set(locale if locale in translations else DEFAULT_LOCALE)
    _current_translation.set(translations[get_locale()])

def get_locale() -> str:
    return _current_locale.get()

def gettext(message: str) -> str:
    return _current_translation.get().ugettext(message)

def ngettext(msgid1: str, msgid2: str, n: int) -> str:
    return _current_translation.get().ngettext(msgid1, msgid2, n)

def lazy_gettext(message: str) -> str:
    return LazyProxy(gettext, message)  # type: ignore[return-value]

def format_datetime(
    datetime: Union[datetime.date, datetime.time],
    format: Optional[str] = None,
    tzinfo: Any = None,
    ) -> str:
    return dates.format_datetime(datetime, format or "medium", tzinfo, get_locale())

def format_date(date: datetime.date, format: Optional[str] = None) -> str:
    return dates.format_date(date, format or "medium", get_locale())

def format_time(
    time: datetime.time,
    format: Optional[str] = None,
    tzinfo: Any = None,
    ) -> str:
    return dates.format_time(time, format or "medium", tzinfo, get_locale())

def get_countries_list() -> List[Tuple[str, str]]:
    locale = Locale.parse(get_locale())
    return [(x, locale.territories[x]) for x in countries_codes]

def get_currencies_list() -> List[Tuple[str, str]]:
    locale = Locale.parse(get_locale())
    return [(str(x), f"{x} - {locale.currencies[x]}") for x in locale.currencies]

def get_locale_display_name(locale: str) -> str:
    return Locale(locale).display_name.capitalize()

@dataclass
class I18nConfig:
    """
    i18n config for your admin interface
    """

    default_locale: str = DEFAULT_LOCALE
    language_cookie_name: Optional[str] = "language"
    language_header_name: Optional[str] = "Accept-Language"
    language_switcher: Optional[List[str]] = None


class LocaleMiddleware:
    def __init__(self, app: ASGIApp, i18n_config: I18nConfig) -> None:
        self.app = app
        self.i18n_config = i18n_config

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        conn = HTTPConnection(scope)
        locale: Optional[str] = self.i18n_config.default_locale
        if (
            self.i18n_config.language_cookie_name
            and conn.cookies.get(self.i18n_config.language_cookie_name, None)
            in SUPPORTED_LOCALES
        ):
            """detect locale in cookies"""
            locale = conn.cookies.get(self.i18n_config.language_cookie_name)
        elif (
            self.i18n_config.language_header_name
            and conn.headers.get(self.i18n_config.language_header_name, None)
            in SUPPORTED_LOCALES
        ):
            """detect locale in headers"""
            locale = conn.headers.get(self.i18n_config.language_header_name)
        set_locale(locale or DEFAULT_LOCALE)
        await self.app(scope, receive, send)
#END ED TRANSLATE

app = Starlette(
 routes=[
  Mount(
   "/static", app=StaticFiles(directory="static"), name="static"
  )
 ],
 on_startup=[lambda: connect(db="aflot_backend", host="mongo", port=27017, username=DB_USERNAME,
        password=DB_PASSWORD)],
 on_shutdown=[lambda: disconnect()],
)

# Create admin
admin = Admin(
    title="Админка АФЛОТ",
    statics_dir="static",
    base_url="/",
    login_logo_url="/statics/logo.svg",  # base_url + '/statics/' + path_to_the_file
    auth_provider=MyAuthProvider(allow_paths=["/statics/logo.svg"]),
    middlewares=[Middleware(SessionMiddleware, secret_key=SECRET)],
    i18n_config = I18nConfig(default_locale="ru")
)


admin.add_view(ModelView(Auth, icon="fa fa-users", label="Пользователи"))
admin.add_view(ModelView(CompanyModel, icon="fa fa-users", label="Компании"))
admin.add_view(ModelView(UserModel, icon="fa fa-users", label="Резюме моряков"))
admin.add_view(ModelView(Vacancy, icon="fa fa-users", label="Вакансии компаний"))
admin.add_view(ModelView(NewsModel, icon="fa fa-blog", label="Новости"))
admin.add_view(ModelView(Contact, icon="fa fa-users", label="Контакты"))
admin.add_view(ModelView(RealHistory, icon="fa fa-blog", label="Истории"))
admin.add_view(ModelView(SwimsTariffs, icon="fa fa-users", label="Тарифы моряков"))
admin.add_view(ModelView(CompanyTariffs, icon="fa fa-users", label="Тарифы компании"))
admin.add_view(ModelView(Navy, icon="fa fa-users", label="Морской флот"))
admin.add_view(ModelView(SettingsGlobal, icon="fa fa-ship", label="Списки"))

admin.mount_to(app)
