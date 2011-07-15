# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).
import inspect
import logging

from configglue.pyschema.schema import (
    BoolOption,
    Section,
    DictOption,
    IntOption,
    ListOption,
    Schema,
    StringOption,
    TupleOption,
)
from django import get_version
from django.conf import global_settings
from django.conf.project_template import settings as project_settings


# As in django.conf.global_settings:
# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s


class UpperCaseDictOption(DictOption):
    """ A DictOption with all upper-case keys. """
    def parse(self, section, parser=None, raw=False):
        parsed = super(UpperCaseDictOption, self).parse(
            section, parser, raw)
        result = {}
        for k, v in parsed.items():
            result[k.upper()] = v
        return result


def derivate_django_schema(schema, exclude=None):
    """Return a modified version of a schema.

    The source schema *must* have a 'version' attribute and
    a 'django' section.

    The resulting schema is almost a copy of the original one, except
    for excluded options in the 'django' section.
    """
    if not exclude:
        return schema

    # create the schema class
    cls = type(schema.__name__, (schema,), {'version': schema.version})
    # include all non-excluded options
    options = {}
    for option in schema().django.options():
        if option.name in exclude:
            continue
        options[option.name] = option
    # create the 'django' section
    django_section = type('django', (Section,), options)
    setattr(cls, 'django', django_section)
    return cls


class BaseDjangoSchema(Schema):
    version = '1.0.2 final'

    # Sections
    class django(Section):

        ################
        # CORE         #
        ################

        debug = BoolOption(default=True)
        template_debug = BoolOption(default=True)
        debug_propagate_exceptions = BoolOption(default=False,
            help="Whether the framework should propagate raw exceptions "
                 "rather than catching them. This is useful under some "
                 "testing situations and should never be used on a live site.")

        use_etags = BoolOption(default=False,
            help="Whether to use the 'Etag' header. This saves bandwidth but "
                 "slows down performance.")

        admins = ListOption(item=TupleOption(length=2), default=[],
            help="People who get code error notifications. In the format "
                 "(('Full Name', 'email@domain.com'), "
                 "('Full Name', 'anotheremail@domain.com'))")

        internal_ips = TupleOption(default=(),
            help="Tuple of IP addresses, as strings, that see debug comments, "
                 "when DEBUG is true and receive x-headers")

        time_zone = StringOption(default='America/Chicago',
            help="Local time zone for this installation. All choices can be "
                 "found here: "
                 "http://en.wikipedia.org/wiki/List_of_tz_zones_by_name "
                 "(although not all systems may support all possibilities)")
        language_code = StringOption(default='en-us',
            help="Language code for this installation. All choices can be "
                 "found here: "
                 "http://www.i18nguy.com/unicode/language-identifiers.html")
        languages = ListOption(
            item=TupleOption(length=2),
            default=[('ar', gettext_noop('Arabic')),
                     ('bn', gettext_noop('Bengali')),
                     ('bg', gettext_noop('Bulgarian')),
                     ('ca', gettext_noop('Catalan')),
                     ('cs', gettext_noop('Czech')),
                     ('cy', gettext_noop('Welsh')),
                     ('da', gettext_noop('Danish')),
                     ('de', gettext_noop('German')),
                     ('el', gettext_noop('Greek')),
                     ('en', gettext_noop('English')),
                     ('es', gettext_noop('Spanish')),
                     ('et', gettext_noop('Estonian')),
                     ('es-ar', gettext_noop('Argentinean Spanish')),
                     ('eu', gettext_noop('Basque')),
                     ('fa', gettext_noop('Persian')),
                     ('fi', gettext_noop('Finnish')),
                     ('fr', gettext_noop('French')),
                     ('ga', gettext_noop('Irish')),
                     ('gl', gettext_noop('Galician')),
                     ('hu', gettext_noop('Hungarian')),
                     ('he', gettext_noop('Hebrew')),
                     ('hi', gettext_noop('Hindi')),
                     ('hr', gettext_noop('Croatian')),
                     ('is', gettext_noop('Icelandic')),
                     ('it', gettext_noop('Italian')),
                     ('ja', gettext_noop('Japanese')),
                     ('ka', gettext_noop('Georgian')),
                     ('ko', gettext_noop('Korean')),
                     ('km', gettext_noop('Khmer')),
                     ('kn', gettext_noop('Kannada')),
                     ('lv', gettext_noop('Latvian')),
                     ('lt', gettext_noop('Lithuanian')),
                     ('mk', gettext_noop('Macedonian')),
                     ('nl', gettext_noop('Dutch')),
                     ('no', gettext_noop('Norwegian')),
                     ('pl', gettext_noop('Polish')),
                     ('pt', gettext_noop('Portuguese')),
                     ('pt-br', gettext_noop('Brazilian Portuguese')),
                     ('ro', gettext_noop('Romanian')),
                     ('ru', gettext_noop('Russian')),
                     ('sk', gettext_noop('Slovak')),
                     ('sl', gettext_noop('Slovenian')),
                     ('sr', gettext_noop('Serbian')),
                     ('sv', gettext_noop('Swedish')),
                     ('ta', gettext_noop('Tamil')),
                     ('te', gettext_noop('Telugu')),
                     ('th', gettext_noop('Thai')),
                     ('tr', gettext_noop('Turkish')),
                     ('uk', gettext_noop('Ukrainian')),
                     ('zh-cn', gettext_noop('Simplified Chinese')),
                     ('zh-tw', gettext_noop('Traditional Chinese'))],
            help="Languages we provide translations for, out of the box. "
                 "The language name should be the utf-8 encoded local name "
                 "for the language")

        languages_bidi = TupleOption(default=('he', 'ar', 'fa'),
            help="Languages using BiDi (right-to-left) layout")

        use_i18n = BoolOption(default=True,
            help="If you set this to False, Django will make some "
                 "optimizations so as not to load the internationalization "
                 "machinery")

        locale_paths = ListOption(item=StringOption())
        language_cookie_name = StringOption(default='django_language')

        managers = ListOption(item=TupleOption(length=2), default=[],
            help="Not-necessarily-technical managers of the site. They get "
                 "broken link notifications and other various e-mails")

        default_content_type = StringOption(default='text/html',
            help="Default content type and charset to use for all "
                 "HttpResponse objects, if a MIME type isn't manually "
                 "specified. These are used to construct the Content-Type "
                 "header")
        default_charset = StringOption(default='utf-8')

        file_charset = StringOption(default='utf-8',
            help="Encoding of files read from disk (template and initial "
                 "SQL files)")

        server_email = StringOption(
            help="E-mail address that error messages come from",
            default='root@localhost')

        send_broken_link_emails = BoolOption(default=False,
            help="Whether to send broken-link e-mails")

        database_engine = StringOption(default='',
            help="'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3'"
                 " or 'oracle'")
        database_name = StringOption(default='',
            help="Or path to database file if using sqlite3")
        database_user = StringOption(default='',
            help="Not used with sqlite3")
        database_password = StringOption(default='',
            help="Not used with sqlite3")
        database_host = StringOption(default='',
            help="Set to empty string for localhost. Not used with sqlite3")
        database_port = StringOption(default='',
            help="Set to empty string for default. Not used with sqlite3")
        database_options = DictOption(
            help="Set to empty dictionary for default")

        email_host = StringOption(default='localhost',
            help="Host for sending e-mail")
        email_port = IntOption(default=25,
            help="Port for sending e-mail")

        email_host_user = StringOption(default='',
            help="Optional SMTP authentication information for EMAIL_HOST")
        email_host_password = StringOption(default='',
            help="Optional SMTP authentication information for EMAIL_HOST")
        email_use_tls = BoolOption(default=False,
            help="Optional SMTP authentication information for EMAIL_HOST")

        installed_apps = ListOption(item=StringOption(),
            default=['django.contrib.auth',
                     'django.contrib.contenttypes',
                     'django.contrib.sessions',
                     'django.contrib.sites'],
            help="List of strings representing installed apps")

        template_dirs = ListOption(item=StringOption(),
            help="List of locations of the template source files, in search "
                 "order")

        template_loaders = ListOption(item=StringOption(),
            default=[
                'django.template.loaders.filesystem.load_template_source',
                'django.template.loaders.app_directories.load_template_source',
            ],
            help="List of callables that know how to import templates from "
                 "various sources")

        template_context_processors = ListOption(
            item=StringOption(),
            default=['django.core.context_processors.auth',
                     'django.core.context_processors.debug',
                     'django.core.context_processors.i18n',
                     'django.core.context_processors.media'],
            help="List of processors used by RequestContext to populate the "
                 "context. Each one should be a callable that takes the "
                 "request object as its only parameter and returns a "
                 "dictionary to add to the context")

        template_string_if_invalid = StringOption(default='',
            help="Output to use in template system for invalid "
                 "(e.g. misspelled) variables")

        admin_media_prefix = StringOption(default='/media/',
            help="URL prefix for admin media -- CSS, JavaScript and images. "
                 "Make sure to use a trailing slash. "
                 "Examples: 'http://foo.com/media/', '/media/'")

        default_from_email = StringOption(
            default='webmaster@localhost',
            help="Default e-mail address to use for various automated "
                 "correspondence from the site managers")
        email_subject_prefix = StringOption(default='[Django] ',
            help="Subject-line prefix for email messages send with "
                 "django.core.mail.mail_admins or ...mail_managers. Make sure "
                 "to include the trailing space")

        append_slash = BoolOption(default=True,
            help="Whether to append trailing slashes to URLs")
        prepend_www = BoolOption(default=False,
            help="Whether to prepend the 'www.' subdomain to URLs that "
                 "don't have it")
        force_script_name = StringOption(null=True,
            help="Override the server-derived value of SCRIPT_NAME")

        disallowed_user_agents = ListOption(
            item=StringOption(),
            default=[],
            help="List of compiled regular expression objects representing "
                 "User-Agent strings that are not allowed to visit any page, "
                 "systemwide. Use this for bad robots/crawlers")

        absolute_url_overrides = DictOption()

        allowed_include_roots = TupleOption(
            help="Tuple of strings representing allowed prefixes for the "
                 "{% ssi %} tag")

        admin_for = ListOption(item=StringOption(),
            help="If this is a admin settings module, this should be a list "
                 "of settings modules (in the format 'foo.bar.baz') for which "
                 "this admin is an admin")

        ignorable_404_starts = ListOption(item=StringOption(),
            default=['/cgi-bin/', '/_vti_bin', '/_vti_inf'],
            help="404s that may be ignored")
        ignorable_404_ends = ListOption(item=StringOption(),
            default=['mail.pl', 'mailform.pl', 'mail.cgi', 'mailform.cgi',
                     'favicon.ico', '.php'])

        secret_key = StringOption(raw=True, default='',
            help="A secret key for this particular Django installation. Used "
                 "in secret-key hashing algorithms. Set this in your "
                 "settings, or Django will complain loudly")

        jing_path = StringOption(default='/usr/bin/jing',
            help="Path to the 'jing' executable -- needed to validate "
                 "XMLFields")

        default_file_storage = StringOption(
            default='django.core.files.storage.FileSystemStorage',
            help="Default file storage mechanism that holds media")

        media_root = StringOption(default='',
            help="Absolute path to the directory that holds media")

        media_url = StringOption(default='',
            help="URL that handles the media served from MEDIA_ROOT")

        file_upload_handlers = ListOption(item=StringOption(),
            default=[
                'django.core.files.uploadhandler.MemoryFileUploadHandler',
                'django.core.files.uploadhandler.TemporaryFileUploadHandler'],
            help="List of upload handler classes to be applied in order")

        file_upload_max_memory_size = IntOption(default=2621440,
            help="Maximum size, in bytes, of a request before it will be "
                 "streamed to the file system instead of into memory")

        file_upload_temp_dir = StringOption(null=True,
            help="Directory in which upload streamed files will be "
                 "temporarily saved. A value of `None` will make Django use "
                 "the operating system's default temporary directory (i.e. "
                 "'/tmp' on *nix systems)")

        file_upload_permissions = StringOption(null=True,
            help="The numeric mode to set newly-uploaded files to. The value "
                 "should be a mode you'd pass directly to os.chmod; "
                 "see http://docs.python.org/lib/os-file-dir.html")

        date_format = StringOption(default='N j, Y',
            help="Default formatting for date objects. See all available "
                 "format strings here: "
                 "http://docs.djangoproject.com/en/dev/ref/templates/builtins/"
                 "#now")

        datetime_format = StringOption(default='N j, Y, P',
            help="Default formatting for datetime objects. See all available "
                 "format strings here: "
                 "http://docs.djangoproject.com/en/dev/ref/templates/builtins/"
                 "#now")

        time_format = StringOption(default='P',
            help="Default formatting for time objects. See all available "
                 "format strings here: "
                 "http://docs.djangoproject.com/en/dev/ref/templates/builtins/"
                 "#now")

        year_month_format = StringOption(default='F Y',
            help="Default formatting for date objects when only the year and "
                 "month are relevant. See all available format strings here: "
                 "http://docs.djangoproject.com/en/dev/ref/templates/builtins/"
                 "#now")

        month_day_format = StringOption(default='F j',
            help="Default formatting for date objects when only the month and "
                 "day are relevant. See all available format strings here: "
                 "http://docs.djangoproject.com/en/dev/ref/templates/builtins/"
                 "#now")

        transactions_managed = BoolOption(default=False,
            help="Do you want to manage transactions manually? "
                 "Hint: you really don't!")

        url_validator_user_agent = StringOption(
            default="Django/%s (http://www.djangoproject.com)" % get_version(),
            help="The User-Agent string to use when checking for URL validity "
                 "through the isExistingURL validator")
        default_tablespace = StringOption(default='',
            help="The tablespaces to use for each model when not "
                 "specified otherwise")
        default_index_tablespace = StringOption(default='',
            help="The tablespaces to use for each model when not "
                 "specified otherwise")

        ##############
        # MIDDLEWARE #
        ##############

        middleware_classes = ListOption(item=StringOption(),
            default=[
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware'],
            help="List of middleware classes to use. Order is important; in "
                 "the request phase, these middleware classes will be applied "
                 "in the order given, and in the response phase the "
                 "middleware will be applied in reverse order")

        ############
        # SESSIONS #
        ############

        session_cookie_name = StringOption(default='sessionid',
            help="Cookie name")
        session_cookie_age = IntOption(default=60 * 60 * 24 * 7 * 2,
            help="Age of cookie, in seconds (default: 2 weeks)")
        session_cookie_domain = StringOption(null=True,
            help="A string like '.lawrence.com', or None for standard "
                 "domain cookie")
        session_cookie_secure = BoolOption(default=False,
            help="Wether the session cookie should be secure (https:// only)")
        session_cookie_path = StringOption(default='/',
            help="The path of the sesion cookie")
        session_save_every_request = BoolOption(default=False,
            help="Whether to save the session data on every request")
        session_expire_at_browser_close = BoolOption(default=False,
            help="Whether a user's session cookie expires when the Web "
                 "browser is closed")
        session_engine = StringOption(
            default='django.contrib.sessions.backends.db',
            help="The module to store session data")
        session_file_path = StringOption(null=True,
            help="Directory to store session files if using the file session "
                 "module. If None, the backend will use a sensible default")

        #########
        # CACHE #
        #########

        cache_backend = StringOption(default='locmem://',
            help="The cache backend to use. See the docstring in "
                 "django.core.cache for the possible values")
        cache_middleware_key_prefix = StringOption(default='')
        cache_middleware_seconds = IntOption(default=600)

        ####################
        # COMMENTS         #
        ####################

        comments_allow_profanities = BoolOption(default=False)
        profanities_list = ListOption(item=StringOption(),
            default=['asshat', 'asshead', 'asshole', 'cunt', 'fuck', 'gook',
                     'nigger', 'shit'],
            help="The profanities that will trigger a validation error in the "
                 "'hasNoProfanities' validator. All of these should be in "
                 "lowercase")
        comments_banned_users_group = StringOption(null=True,
            help="The group ID that designates which users are banned. "
                 "Set to None if you're not using it")
        comments_moderators_group = StringOption(null=True,
            help="The group ID that designates which users can moderate "
                 "comments. Set to None if you're not using it")
        comments_sketchy_users_group = StringOption(null=True,
            help="The group ID that designates the users whose comments "
                 "should be e-mailed to MANAGERS. Set to None if you're not "
                 "using it")
        comments_first_few = IntOption(default=0,
            help="The system will e-mail MANAGERS the first "
                 "COMMENTS_FIRST_FEW comments by each user. Set this to 0 if "
                 "you want to disable it")
        banned_ips = TupleOption(
            help="A tuple of IP addresses that have been banned from "
                 "participating in various Django-powered features")

        ##################
        # AUTHENTICATION #
        ##################

        authentication_backends = ListOption(
            item=StringOption(),
            default=['django.contrib.auth.backends.ModelBackend'])
        login_url = StringOption(default='/accounts/login/')
        logout_url = StringOption(default='/accounts/logout/')
        login_redirect_url = StringOption(default='/accounts/profile/')
        password_reset_timeout_days = IntOption(default=3,
            help="The number of days a password reset link is valid for")

        ###########
        # TESTING #
        ###########

        test_runner = StringOption(
            default='django.test.simple.run_tests',
            help="The name of the method to use to invoke the test suite")
        test_database_name = StringOption(null=True,
            help="The name of the database to use for testing purposes. "
                 "If None, a name of 'test_' + DATABASE_NAME will be assumed")
        test_database_charset = StringOption(null=True,
            help="Strings used to set the character set and collation order "
                 "for the test database. These values are passed literally to "
                 "the server, so they are backend-dependent. If None, no "
                 "special settings are sent (system defaults are used)")
        test_database_collation = StringOption(null=True,
            help="Strings used to set the character set and collation order "
                 "for the test database. These values are passed literally to "
                 "the server, so they are backend-dependent. If None, no "
                 "special settings are sent (system defaults are used)")

        ############
        # FIXTURES #
        ############

        fixture_dirs = ListOption(item=StringOption(),
            help="The list of directories to search for fixtures")

        ####################
        # PROJECT TEMPLATE #
        ####################

        site_id = IntOption(default=1)
        root_urlconf = StringOption(default='{{ project_name }}.urls')


Django112Base = derivate_django_schema(
    BaseDjangoSchema, exclude=['jing_path'])


class Django112Schema(Django112Base):
    version = '1.1.2'

    # sections
    class django(Django112Base.django):

        ################
        # CORE         #
        ################

        # update default value
        languages = ListOption(
            item=TupleOption(length=2),
            help="Languages we provide translations for, out of the box. "
                 "The language name should be the utf-8 encoded local name "
                 "for the language",
            default=[
                ('ar', gettext_noop('Arabic')),
                ('bg', gettext_noop('Bulgarian')),
                ('bn', gettext_noop('Bengali')),
                ('bs', gettext_noop('Bosnian')),
                ('ca', gettext_noop('Catalan')),
                ('cs', gettext_noop('Czech')),
                ('cy', gettext_noop('Welsh')),
                ('da', gettext_noop('Danish')),
                ('de', gettext_noop('German')),
                ('el', gettext_noop('Greek')),
                ('en', gettext_noop('English')),
                ('es', gettext_noop('Spanish')),
                ('es-ar', gettext_noop('Argentinean Spanish')),
                ('et', gettext_noop('Estonian')),
                ('eu', gettext_noop('Basque')),
                ('fa', gettext_noop('Persian')),
                ('fi', gettext_noop('Finnish')),
                ('fr', gettext_noop('French')),
                ('fy-nl', gettext_noop('Frisian')),
                ('ga', gettext_noop('Irish')),
                ('gl', gettext_noop('Galician')),
                ('he', gettext_noop('Hebrew')),
                ('hi', gettext_noop('Hindi')),
                ('hr', gettext_noop('Croatian')),
                ('hu', gettext_noop('Hungarian')),
                ('is', gettext_noop('Icelandic')),
                ('it', gettext_noop('Italian')),
                ('ja', gettext_noop('Japanese')),
                ('ka', gettext_noop('Georgian')),
                ('km', gettext_noop('Khmer')),
                ('kn', gettext_noop('Kannada')),
                ('ko', gettext_noop('Korean')),
                ('lt', gettext_noop('Lithuanian')),
                ('lv', gettext_noop('Latvian')),
                ('mk', gettext_noop('Macedonian')),
                ('nl', gettext_noop('Dutch')),
                ('no', gettext_noop('Norwegian')),
                ('pl', gettext_noop('Polish')),
                ('pt', gettext_noop('Portuguese')),
                ('pt-br', gettext_noop('Brazilian Portuguese')),
                ('ro', gettext_noop('Romanian')),
                ('ru', gettext_noop('Russian')),
                ('sk', gettext_noop('Slovak')),
                ('sl', gettext_noop('Slovenian')),
                ('sq', gettext_noop('Albanian')),
                ('sr', gettext_noop('Serbian')),
                ('sr-latn', gettext_noop('Serbian Latin')),
                ('sv', gettext_noop('Swedish')),
                ('ta', gettext_noop('Tamil')),
                ('te', gettext_noop('Telugu')),
                ('th', gettext_noop('Thai')),
                ('tr', gettext_noop('Turkish')),
                ('uk', gettext_noop('Ukrainian')),
                ('zh-cn', gettext_noop('Simplified Chinese')),
                ('zh-tw', gettext_noop('Traditional Chinese')),
            ])


class Django125Schema(Django112Schema):
    version = '1.2.5'

    # sections
    class django(Django112Schema.django):

        ################
        # CORE         #
        ################

        # update default value
        languages = ListOption(
            item=TupleOption(length=2),
            help="Languages we provide translations for, out of the box. "
                 "The language name should be the utf-8 encoded local name "
                 "for the language",
            default=[
                ('ar', gettext_noop('Arabic')),
                ('bg', gettext_noop('Bulgarian')),
                ('bn', gettext_noop('Bengali')),
                ('bs', gettext_noop('Bosnian')),
                ('ca', gettext_noop('Catalan')),
                ('cs', gettext_noop('Czech')),
                ('cy', gettext_noop('Welsh')),
                ('da', gettext_noop('Danish')),
                ('de', gettext_noop('German')),
                ('el', gettext_noop('Greek')),
                ('en', gettext_noop('English')),
                ('en-gb', gettext_noop('British English')),
                ('es', gettext_noop('Spanish')),
                ('es-ar', gettext_noop('Argentinian Spanish')),
                ('et', gettext_noop('Estonian')),
                ('eu', gettext_noop('Basque')),
                ('fa', gettext_noop('Persian')),
                ('fi', gettext_noop('Finnish')),
                ('fr', gettext_noop('French')),
                ('fy-nl', gettext_noop('Frisian')),
                ('ga', gettext_noop('Irish')),
                ('gl', gettext_noop('Galician')),
                ('he', gettext_noop('Hebrew')),
                ('hi', gettext_noop('Hindi')),
                ('hr', gettext_noop('Croatian')),
                ('hu', gettext_noop('Hungarian')),
                ('id', gettext_noop('Indonesian')),
                ('is', gettext_noop('Icelandic')),
                ('it', gettext_noop('Italian')),
                ('ja', gettext_noop('Japanese')),
                ('ka', gettext_noop('Georgian')),
                ('km', gettext_noop('Khmer')),
                ('kn', gettext_noop('Kannada')),
                ('ko', gettext_noop('Korean')),
                ('lt', gettext_noop('Lithuanian')),
                ('lv', gettext_noop('Latvian')),
                ('mk', gettext_noop('Macedonian')),
                ('ml', gettext_noop('Malayalam')),
                ('mn', gettext_noop('Mongolian')),
                ('nl', gettext_noop('Dutch')),
                ('no', gettext_noop('Norwegian')),
                ('nb', gettext_noop('Norwegian Bokmal')),
                ('nn', gettext_noop('Norwegian Nynorsk')),
                ('pl', gettext_noop('Polish')),
                ('pt', gettext_noop('Portuguese')),
                ('pt-br', gettext_noop('Brazilian Portuguese')),
                ('ro', gettext_noop('Romanian')),
                ('ru', gettext_noop('Russian')),
                ('sk', gettext_noop('Slovak')),
                ('sl', gettext_noop('Slovenian')),
                ('sq', gettext_noop('Albanian')),
                ('sr', gettext_noop('Serbian')),
                ('sr-latn', gettext_noop('Serbian Latin')),
                ('sv', gettext_noop('Swedish')),
                ('ta', gettext_noop('Tamil')),
                ('te', gettext_noop('Telugu')),
                ('th', gettext_noop('Thai')),
                ('tr', gettext_noop('Turkish')),
                ('uk', gettext_noop('Ukrainian')),
                ('vi', gettext_noop('Vietnamese')),
                ('zh-cn', gettext_noop('Simplified Chinese')),
                ('zh-tw', gettext_noop('Traditional Chinese')),
            ])

        use_l10n = BoolOption(
            default=True,
            help="If you set this to False, Django will not format dates, "
                "numbers and calendars according to the current locale")

        databases = DictOption(
            item=UpperCaseDictOption(spec={
                'engine': StringOption(default='django.db.backends.'),
                'name': StringOption(),
                'user': StringOption(),
                'password': StringOption(),
                'host': StringOption(),
                'port': StringOption(),
            }),
            default={
                'default': {
                    'ENGINE': 'django.db.backends.',
                    'NAME': '',
                    'USER': '',
                    'PASSWORD': '',
                    'HOST': '',
                    'PORT': '',
                }
            })
        database_routers = ListOption(
            item=StringOption(),
            help="Classes used to implement db routing behaviour")

        email_backend = StringOption(
            default='django.core.mail.backends.smtp.EmailBackend',
            help="The email backend to use. For possible shortcuts see "
                "django.core.mail. The default is to use the SMTP backend. "
                "Third party backends can be specified by providing a Python "
                "path to a module that defines an EmailBackend class.")

        installed_apps = ListOption(item=StringOption(),
            help="List of strings representing installed apps",
            default=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.messages',
            ])

        template_loaders = ListOption(item=StringOption(),
            help="List of callables that know how to import templates from "
                 "various sources",
            default=[
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ])

        template_context_processors = ListOption(
            item=StringOption(),
            help="List of processors used by RequestContext to populate the "
                 "context. Each one should be a callable that takes the "
                 "request object as its only parameter and returns a "
                 "dictionary to add to the context",
            default=[
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.contrib.messages.context_processors.messages',
            ])

        format_module_path = StringOption(
            null=True, default=None,
            help="Python module path where user will place custom format "
                "definition. The directory where this setting is pointing "
                "should contain subdirectories named as the locales, "
                "containing a formats.py file")
        short_date_format = StringOption(
            default='m/d/Y',
            help="Default short formatting for date objects")
        short_datetime_format = StringOption(
            default='m/d/Y P',
            help="Default short formatting for datetime objects")
        date_input_formats = ListOption(
            item=StringOption(),
            default=[
                # '2006-10-25', '10/25/2006', '10/25/06'
                '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
                # 'Oct 25 2006', 'Oct 25, 2006'
                '%b %d %Y', '%b %d, %Y',
                # '25 Oct 2006', '25 Oct, 2006'
                '%d %b %Y', '%d %b, %Y',
                # 'October 25 2006', 'October 25, 2006'
                '%B %d %Y', '%B %d, %Y',
                # '25 October 2006', '25 October, 2006'
                '%d %B %Y', '%d %B, %Y',
            ],
            help="Default formats to be used when parsing dates from input "
                "boxes, in order")
        time_input_formats = ListOption(
            item=StringOption(),
            default=[
                '%H:%M:%S',     # '14:30:59'
                '%H:%M',         # '14:30'
            ],
            help="Default formats to be used when parsing times from input "
                "boxes, in order")
        datetime_input_formats = ListOption(
            item=StringOption(),
            default=[
                '%Y-%m-%d %H:%M:%S',      # '2006-10-25 14:30:59'
                '%Y-%m-%d %H:%M',         # '2006-10-25 14:30'
                '%Y-%m-%d',               # '2006-10-25'
                '%m/%d/%Y %H:%M:%S',      # '10/25/2006 14:30:59'
                '%m/%d/%Y %H:%M',         # '10/25/2006 14:30'
                '%m/%d/%Y',               # '10/25/2006'
                '%m/%d/%y %H:%M:%S',      # '10/25/06 14:30:59'
                '%m/%d/%y %H:%M',         # '10/25/06 14:30'
                '%m/%d/%y',               # '10/25/06'
            ],
            help="Default formats to be used when parsing dates and times "
                "from input boxes, in order")

        first_day_of_week = IntOption(
            default=0,
            help="First day of week, to be used on calendars. 0 means Sunday, "
                "1 means Monday...")
        decimal_separator = StringOption(
            default='.',
            help="Decimal separator symbol")
        use_thousand_separator = BoolOption(
            default=False,
            help="Boolean that sets whether to add thousand separator when "
                "formatting numbers")
        number_grouping = IntOption(
            default=0,
            help="Number of digits that will be together, when splitting them "
                "by THOUSAND_SEPARATOR. 0 means no grouping, 3 means "
                "splitting by thousands...")
        thousand_separator = StringOption(
            default=',',
            help="Thousand separator symbol")

        ##############
        # MIDDLEWARE #
        ##############

        middleware_classes = ListOption(item=StringOption(),
            help="List of middleware classes to use. Order is important; in "
                 "the request phase, these middleware classes will be applied "
                 "in the order given, and in the response phase the "
                 "middleware will be applied in reverse order",
            default=[
                'django.middleware.common.CommonMiddleware',
                'django.contrib.sessions.middleware.SessionMiddleware',
                'django.middleware.csrf.CsrfViewMiddleware',
                'django.contrib.auth.middleware.AuthenticationMiddleware',
                'django.contrib.messages.middleware.MessageMiddleware',
            ])

        ########
        # CSRF #
        ########

        csrf_failure_view = StringOption(
            default='django.views.csrf.csrf_failure',
            help="Dotted path to callable to be used as view when a request "
                "is rejected by the CSRF middleware")
        csrf_cookie_name = StringOption(
            default='csrftoken',
            help="Name for CSRF cookie")
        csrf_cookie_domain = StringOption(
            null=True,
            help="Domain for CSRF cookie")

        ############
        # MESSAGES #
        ############

        message_storage = StringOption(
            default='django.contrib.messages.storage.user_messages.'
                'LegacyFallbackStorage',
            help="Class to be used as messages backend")

        ###########
        # TESTING #
        ###########

        test_runner = StringOption(
            default='django.test.simple.DjangoTestSuiteRunner',
            help="The name of the class to use to run the test suite")


Django13Base = derivate_django_schema(
    Django125Schema, exclude=['cache_backend'])


class Django13Schema(Django13Base):
    version = '1.3'

    # sections
    class django(Django13Base.django):

        ################
        # CORE         #
        ################

        # update default value
        languages = ListOption(
            item=TupleOption(length=2),
            help="Languages we provide translations for, out of the box. "
                 "The language name should be the utf-8 encoded local name "
                 "for the language",
            default=[
                ('ar', gettext_noop('Arabic')),
                ('az', gettext_noop('Azerbaijani')),
                ('bg', gettext_noop('Bulgarian')),
                ('bn', gettext_noop('Bengali')),
                ('bs', gettext_noop('Bosnian')),
                ('ca', gettext_noop('Catalan')),
                ('cs', gettext_noop('Czech')),
                ('cy', gettext_noop('Welsh')),
                ('da', gettext_noop('Danish')),
                ('de', gettext_noop('German')),
                ('el', gettext_noop('Greek')),
                ('en', gettext_noop('English')),
                ('en-gb', gettext_noop('British English')),
                ('es', gettext_noop('Spanish')),
                ('es-ar', gettext_noop('Argentinian Spanish')),
                ('es-mx', gettext_noop('Mexican Spanish')),
                ('es-ni', gettext_noop('Nicaraguan Spanish')),
                ('et', gettext_noop('Estonian')),
                ('eu', gettext_noop('Basque')),
                ('fa', gettext_noop('Persian')),
                ('fi', gettext_noop('Finnish')),
                ('fr', gettext_noop('French')),
                ('fy-nl', gettext_noop('Frisian')),
                ('ga', gettext_noop('Irish')),
                ('gl', gettext_noop('Galician')),
                ('he', gettext_noop('Hebrew')),
                ('hi', gettext_noop('Hindi')),
                ('hr', gettext_noop('Croatian')),
                ('hu', gettext_noop('Hungarian')),
                ('id', gettext_noop('Indonesian')),
                ('is', gettext_noop('Icelandic')),
                ('it', gettext_noop('Italian')),
                ('ja', gettext_noop('Japanese')),
                ('ka', gettext_noop('Georgian')),
                ('km', gettext_noop('Khmer')),
                ('kn', gettext_noop('Kannada')),
                ('ko', gettext_noop('Korean')),
                ('lt', gettext_noop('Lithuanian')),
                ('lv', gettext_noop('Latvian')),
                ('mk', gettext_noop('Macedonian')),
                ('ml', gettext_noop('Malayalam')),
                ('mn', gettext_noop('Mongolian')),
                ('nl', gettext_noop('Dutch')),
                ('no', gettext_noop('Norwegian')),
                ('nb', gettext_noop('Norwegian Bokmal')),
                ('nn', gettext_noop('Norwegian Nynorsk')),
                ('pa', gettext_noop('Punjabi')),
                ('pl', gettext_noop('Polish')),
                ('pt', gettext_noop('Portuguese')),
                ('pt-br', gettext_noop('Brazilian Portuguese')),
                ('ro', gettext_noop('Romanian')),
                ('ru', gettext_noop('Russian')),
                ('sk', gettext_noop('Slovak')),
                ('sl', gettext_noop('Slovenian')),
                ('sq', gettext_noop('Albanian')),
                ('sr', gettext_noop('Serbian')),
                ('sr-latn', gettext_noop('Serbian Latin')),
                ('sv', gettext_noop('Swedish')),
                ('ta', gettext_noop('Tamil')),
                ('te', gettext_noop('Telugu')),
                ('th', gettext_noop('Thai')),
                ('tr', gettext_noop('Turkish')),
                ('uk', gettext_noop('Ukrainian')),
                ('ur', gettext_noop('Urdu')),
                ('vi', gettext_noop('Vietnamese')),
                ('zh-cn', gettext_noop('Simplified Chinese')),
                ('zh-tw', gettext_noop('Traditional Chinese')),
            ])

        installed_apps = ListOption(item=StringOption(),
            help="List of strings representing installed apps",
            default=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.sites',
                'django.contrib.messages',
                'django.contrib.staticfiles',
            ])

        template_context_processors = ListOption(
            item=StringOption(),
            help="List of processors used by RequestContext to populate the "
                 "context. Each one should be a callable that takes the "
                 "request object as its only parameter and returns a "
                 "dictionary to add to the context",
            default=[
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ])

        static_root = StringOption(
            default='',
            help='Absolute path to the directory that holds static files.')

        static_url = StringOption(
            null=True, default='/static/',
            help='URL that handles the static files served from STATIC_ROOT.')

        ############
        # SESSIONS #
        ############

        session_cookie_httponly = BoolOption(
            default=False,
            help="Whether to use the non-RFC standard htt pOnly flag (IE, "
                 "FF3+, others)")

        #########
        # CACHE #
        #########

        caches = DictOption()
        cache_middleware_alias = StringOption(default='default')

        ############
        # COMMENTS #
        ############

        profanities_list = ListOption(item=StringOption(),
            default=[],
            help="The profanities that will trigger a validation error in the "
                 "'hasNoProfanities' validator. All of these should be in "
                 "lowercase")

        ###########
        # LOGGING #
        ###########

        logging_config = StringOption(
            default='django.utils.log.dictConfig',
            help='The callable to use to configure logging')
        logging = DictOption(
            spec={
                'version': IntOption(default=1),
                'disable_existing_loggers': BoolOption(default=False),
                'handlers': DictOption(spec={
                    'mail_admins': DictOption(spec={
                        'level': StringOption(default='ERROR'),
                        'class': StringOption(
                            default='django.utils.log.AdminEmailHandler'),
                    }),
                }),
                'loggers': DictOption(
                    spec={
                        'django.request': DictOption(
                            spec={
                                'handlers': ListOption(
                                    item=StringOption(),
                                    default=['mail_admins']),
                                'level': StringOption(default='ERROR'),
                                'propagate': BoolOption(default=True),
                            }),
                    }),
            },
            help="The default logging configuration. This sends an email to "
                 "the site admins on every HTTP 500 error. All other records "
                 "are sent to the bit bucket.")

        ###############
        # STATICFILES #
        ###############

        staticfiles_dirs = ListOption(
            item=StringOption(),
            help='A list of locations of additional static files')
        staticfiles_storage = StringOption(
            default='django.contrib.staticfiles.storage.StaticFilesStorage',
            help='The default file storage backend used during the build '
                 'process')
        staticfiles_finders = ListOption(
            item=StringOption(),
            default=[
                'django.contrib.staticfiles.finders.FileSystemFinder',
                'django.contrib.staticfiles.finders.AppDirectoriesFinder',
            ],
            help='List of finder classes that know how to find static files '
                 'in various locations.')

        admin_media_prefix = StringOption(default='/static/admin/',
            help="URL prefix for admin media -- CSS, JavaScript and images. "
                 "Make sure to use a trailing slash. "
                 "Examples: 'http://foo.com/media/', '/media/'")


class DjangoSchemaFactory(object):
    def __init__(self):
        self._schemas = {}

    def register(self, schema_cls, version=None):
        if version is None:
            # fall back to looking the version of the schema class
            version = getattr(schema_cls, 'version', None)
        if version is None:
            raise ValueError(
                "No version was specified nor found in schema %r" % schema_cls)
        self._schemas[version] = schema_cls

    def get(self, version, strict=True):
        if version in self._schemas:
            return self._schemas[version]

        msg = "No schema registered for version %r" % version
        if strict:
            raise ValueError(msg)
        else:
            logging.warn(msg)

        logging.warn("Dynamically creating schema for version %r" % version)
        schema = self.build(version)
        return schema

    def build(self, version_string=None, options=None):
        if version_string is None:
            version_string = get_version()
        if options is None:
            options = dict([(name.lower(), value) for (name, value) in
                inspect.getmembers(global_settings) if name.isupper()])
            project_options = dict([(name.lower(), value) for (name, value) in
                inspect.getmembers(project_settings) if name.isupper()])
            options.update(project_options)

        class DjangoSchema(Schema):
            version = version_string

            class django(Section):
                pass

        def get_option_type(name, value):
            type_mappings = {
                int: IntOption,
                bool: BoolOption,
                list: ListOption,
                tuple: TupleOption,
                dict: DictOption,
                str: StringOption,
                unicode: StringOption,
            }
            if value is None:
                return StringOption(name=name, default=value, null=True)
            else:
                option_type = type_mappings[type(value)]
                kwargs = {'name': name, 'default': value}

                if option_type in (DictOption, ListOption):
                    # get inner item type
                    if option_type == DictOption:
                        items = value.values()
                    else:
                        items = value

                    item_type = None
                    if items:
                        item_type = type_mappings.get(type(items[0]), None)
                        # make sure all items have a consistent type
                        for item in items:
                            current_item_type = type_mappings.get(
                                type(item), None)
                            if current_item_type != item_type:
                                item_type = None
                                # mismatching types found. fallback to default
                                # item type
                                break
                    if item_type is not None:
                        kwargs['item'] = item_type()

                return option_type(**kwargs)

        for name, value in options.items():
            if name == '__CONFIGGLUE_PARSER__':
                continue
            option = get_option_type(name, value)
            setattr(DjangoSchema.django, name, option)

        # register schema for it to be available during next query
        self.register(DjangoSchema, version_string)
        return DjangoSchema


schemas = DjangoSchemaFactory()
schemas.register(BaseDjangoSchema, '1.0.2 final')
schemas.register(BaseDjangoSchema, '1.0.4')
schemas.register(Django112Schema)
schemas.register(Django112Schema, '1.1.4')
schemas.register(Django125Schema)
schemas.register(Django13Schema)
