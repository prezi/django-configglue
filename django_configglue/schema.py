# Copyright 2010 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).
import logging
from copy import deepcopy

from configglue.pyschema.schema import (
    BoolConfigOption,
    ConfigSection,
    DictConfigOption,
    IntConfigOption,
    LinesConfigOption,
    Schema,
    StringConfigOption,
    TupleConfigOption,
)
from django import get_version


# As in django.conf.global_settings:
# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s


class UpperCaseDictConfigOption(DictConfigOption):
    """ A DictConfigOption with all upper-case keys. """
    def parse(self, section, parser=None, raw=False):
        parsed = super(UpperCaseDictConfigOption, self).parse(
            section, parser, raw)
        result = {}
        for k, v in parsed.items():
            result[k.upper()] = v
        return result


class BaseDjangoSchema(Schema):
    version = '1.0.2 final'

    # Sections
    django = ConfigSection('django')

    ################
    # CORE         #
    ################

    django.debug = BoolConfigOption(default=True)
    django.template_debug = BoolConfigOption(default=True)
    django.debug_propagate_exceptions = BoolConfigOption(default=False,
        help="Whether the framework should propagate raw exceptions rather "
             "than catching them. This is useful under some testing "
             "situations and should never be used on a live site.")

    django.use_etags = BoolConfigOption(default=False,
        help="Whether to use the 'Etag' header. This saves bandwidth but "
             "slows down performance.")

    django.admins = LinesConfigOption(item=TupleConfigOption(2), default=[],
        help="People who get code error notifications. In the format "
             "(('Full Name', 'email@domain.com'), "
             "('Full Name', 'anotheremail@domain.com'))")

    django.internal_ips = TupleConfigOption(default=(),
        help="Tuple of IP addresses, as strings, that see debug comments, "
             "when DEBUG is true and receive x-headers")

    django.time_zone = StringConfigOption(default='America/Chicago',
        help="Local time zone for this installation. All choices can be found "
             "here: http://en.wikipedia.org/wiki/List_of_tz_zones_by_name "
             "(although not all systems may support all possibilities)")
    django.language_code = StringConfigOption(default='en-us',
        help="Language code for this installation. All choices can be found "
             "here: http://www.i18nguy.com/unicode/language-identifiers.html")
    django.languages = LinesConfigOption(
        item=TupleConfigOption(length=2),
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

    django.languages_bidi = TupleConfigOption(default=('he', 'ar', 'fa'),
        help="Languages using BiDi (right-to-left) layout")

    django.use_i18n = BoolConfigOption(default=True,
        help="If you set this to False, Django will make some optimizations "
             "so as not to load the internationalization machinery")

    django.locale_paths = LinesConfigOption(item=StringConfigOption())
    django.language_cookie_name = StringConfigOption(default='django_language')

    django.managers = LinesConfigOption(item=TupleConfigOption(2), default=[],
        help="Not-necessarily-technical managers of the site. They get broken "
             "link notifications and other various e-mails")

    django.default_content_type = StringConfigOption(default='text/html',
        help="Default content type and charset to use for all HttpResponse "
             "objects, if a MIME type isn't manually specified. These are "
             "used to construct the Content-Type header")
    django.default_charset = StringConfigOption(default='utf-8')

    django.file_charset = StringConfigOption(default='utf-8',
        help="Encoding of files read from disk (template and initial "
             "SQL files)")

    django.server_email = StringConfigOption(
        help="E-mail address that error messages come from",
        default='root@localhost')

    django.send_broken_link_emails = BoolConfigOption(default=False,
        help="Whether to send broken-link e-mails")

    django.database_engine = StringConfigOption(default='',
        help="'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3'"
             " or 'oracle'")
    django.database_name = StringConfigOption(default='',
        help="Or path to database file if using sqlite3")
    django.database_user = StringConfigOption(default='',
        help="Not used with sqlite3")
    django.database_password= StringConfigOption(default='',
        help="Not used with sqlite3")
    django.database_host = StringConfigOption(default='',
        help="Set to empty string for localhost. Not used with sqlite3")
    django.database_port = StringConfigOption(default='',
        help="Set to empty string for default. Not used with sqlite3")
    django.database_options = DictConfigOption(
        help="Set to empty dictionary for default")

    django.email_host = StringConfigOption(default='localhost',
        help="Host for sending e-mail")
    django.email_port = IntConfigOption(default=25,
        help="Port for sending e-mail")

    django.email_host_user = StringConfigOption(default='',
        help="Optional SMTP authentication information for EMAIL_HOST")
    django.email_host_password = StringConfigOption(default='',
        help="Optional SMTP authentication information for EMAIL_HOST")
    django.email_use_tls = BoolConfigOption(default=False,
        help="Optional SMTP authentication information for EMAIL_HOST")

    django.installed_apps = LinesConfigOption(item=StringConfigOption(),
        default=['django.contrib.auth',
                 'django.contrib.contenttypes',
                 'django.contrib.sessions',
                 'django.contrib.sites'],
        help="List of strings representing installed apps")

    django.template_dirs = LinesConfigOption(item=StringConfigOption(),
        help="List of locations of the template source files, in search order")

    django.template_loaders = LinesConfigOption(item=StringConfigOption(),
        default=['django.template.loaders.filesystem.load_template_source',
                 'django.template.loaders.app_directories.load_template_source'],
        help="List of callables that know how to import templates from "
             "various sources")

    django.template_context_processors = LinesConfigOption(
        item=StringConfigOption(),
        default=['django.core.context_processors.auth',
                 'django.core.context_processors.debug',
                 'django.core.context_processors.i18n',
                 'django.core.context_processors.media'],
        help="List of processors used by RequestContext to populate the "
             "context. Each one should be a callable that takes the request "
             "object as its only parameter and returns a dictionary to add to "
             "the context")

    django.template_string_if_invalid = StringConfigOption(default='',
        help="Output to use in template system for invalid "
             "(e.g. misspelled) variables")

    django.admin_media_prefix = StringConfigOption(default='/media/',
        help="URL prefix for admin media -- CSS, JavaScript and images. "
             "Make sure to use a trailing slash. "
             "Examples: 'http://foo.com/media/', '/media/'")

    django.default_from_email = StringConfigOption(
        default='webmaster@localhost',
        help="Default e-mail address to use for various automated "
             "correspondence from the site managers")
    django.email_subject_prefix = StringConfigOption(default='[Django] ',
        help="Subject-line prefix for email messages send with "
             "django.core.mail.mail_admins or ...mail_managers. Make sure to "
             "include the trailing space")

    django.append_slash = BoolConfigOption(default=True,
        help="Whether to append trailing slashes to URLs")
    django.prepend_www = BoolConfigOption(default=False,
        help="Whether to prepend the 'www.' subdomain to URLs that "
             "don't have it")
    django.force_script_name = StringConfigOption(null=True,
        help="Override the server-derived value of SCRIPT_NAME")

    django.disallowed_user_agents = LinesConfigOption(
        item=StringConfigOption(),
        default=[],
        help="List of compiled regular expression objects representing "
             "User-Agent strings that are not allowed to visit any page, "
             "systemwide. Use this for bad robots/crawlers")

    django.absolute_url_overrides = DictConfigOption()

    django.allowed_include_roots = TupleConfigOption(
        help="Tuple of strings representing allowed prefixes for the "
             "{% ssi %} tag")

    django.admin_for = LinesConfigOption(item=StringConfigOption(),
        help="If this is a admin settings module, this should be a list of "
             "settings modules (in the format 'foo.bar.baz') for which this "
             "admin is an admin")

    django.ignorable_404_starts = LinesConfigOption(item=StringConfigOption(),
        default=['/cgi-bin/', '/_vti_bin', '/_vti_inf'],
        help="404s that may be ignored")
    django.ignorable_404_ends = LinesConfigOption(item=StringConfigOption(),
        default=['mail.pl', 'mailform.pl', 'mail.cgi', 'mailform.cgi',
                 'favicon.ico', '.php'])

    django.secret_key = StringConfigOption(raw=True, default='',
        help="A secret key for this particular Django installation. Used in "
             "secret-key hashing algorithms. Set this in your settings, or "
             "Django will complain loudly")

    django.jing_path = StringConfigOption(default='/usr/bin/jing',
        help="Path to the 'jing' executable -- needed to validate XMLFields")

    django.default_file_storage = StringConfigOption(
        default='django.core.files.storage.FileSystemStorage',
        help="Default file storage mechanism that holds media")

    django.media_root = StringConfigOption(default='',
        help="Absolute path to the directory that holds media")

    django.media_url = StringConfigOption(default='',
        help="URL that handles the media served from MEDIA_ROOT")

    django.file_upload_handlers = LinesConfigOption(item=StringConfigOption(),
        default=['django.core.files.uploadhandler.MemoryFileUploadHandler',
                 'django.core.files.uploadhandler.TemporaryFileUploadHandler'],
        help="List of upload handler classes to be applied in order")

    django.file_upload_max_memory_size = IntConfigOption(default=2621440,
        help="Maximum size, in bytes, of a request before it will be streamed "
             "to the file system instead of into memory")

    django.file_upload_temp_dir = StringConfigOption(null=True,
        help="Directory in which upload streamed files will be temporarily "
             "saved. A value of `None` will make Django use the operating "
             "system's default temporary directory (i.e. '/tmp' on *nix "
             "systems)")

    django.file_upload_permissions = StringConfigOption(null=True,
        help="The numeric mode to set newly-uploaded files to. The value "
             "should be a mode you'd pass directly to os.chmod; "
             "see http://docs.python.org/lib/os-file-dir.html")

    django.date_format = StringConfigOption(default='N j, Y',
        help="Default formatting for date objects. See all available format "
             "strings here: "
             "http://docs.djangoproject.com/en/dev/ref/templates/builtins/#now")

    django.datetime_format = StringConfigOption(default='N j, Y, P',
        help="Default formatting for datetime objects. See all available "
             "format strings here: "
             "http://docs.djangoproject.com/en/dev/ref/templates/builtins/#now")

    django.time_format = StringConfigOption(default='P',
        help="Default formatting for time objects. See all available format "
             "strings here: "
             "http://docs.djangoproject.com/en/dev/ref/templates/builtins/#now")

    django.year_month_format = StringConfigOption(default='F Y',
        help="Default formatting for date objects when only the year and "
             "month are relevant. See all available format strings here: "
             "http://docs.djangoproject.com/en/dev/ref/templates/builtins/#now")

    django.month_day_format = StringConfigOption(default='F j',
        help="Default formatting for date objects when only the month and "
             "day are relevant. See all available format strings here: "
             "http://docs.djangoproject.com/en/dev/ref/templates/builtins/#now")

    django.transactions_managed = BoolConfigOption(default=False,
        help="Do you want to manage transactions manually? "
             "Hint: you really don't!")

    django.url_validator_user_agent = StringConfigOption(
        default="Django/%s (http://www.djangoproject.com)" % get_version(),
        help="The User-Agent string to use when checking for URL validity "
             "through the isExistingURL validator")
    django.default_tablespace = StringConfigOption(default='',
        help="The tablespaces to use for each model when not "
             "specified otherwise")
    django.default_index_tablespace = StringConfigOption(default='',
        help="The tablespaces to use for each model when not "
             "specified otherwise")

    ##############
    # MIDDLEWARE #
    ##############

    django.middleware_classes = LinesConfigOption(item=StringConfigOption(),
        default=['django.middleware.common.CommonMiddleware',
                 'django.contrib.sessions.middleware.SessionMiddleware',
                 'django.contrib.auth.middleware.AuthenticationMiddleware'],
        help="List of middleware classes to use. Order is important; in the "
             "request phase, these middleware classes will be applied in the "
             "order given, and in the response phase the middleware will be "
             "applied in reverse order")

    ############
    # SESSIONS #
    ############

    django.session_cookie_name = StringConfigOption(default='sessionid',
        help="Cookie name")
    django.session_cookie_age = IntConfigOption(default=60*60*24*7*2,
        help="Age of cookie, in seconds (default: 2 weeks)")
    django.session_cookie_domain = StringConfigOption(null=True,
        help="A string like '.lawrence.com', or None for standard "
             "domain cookie")
    django.session_cookie_secure = BoolConfigOption(default=False, 
        help="Wether the session cookie should be secure (https:// only)")
    django.session_cookie_path = StringConfigOption(default='/',
        help="The path of the sesion cookie")
    django.session_save_every_request = BoolConfigOption(default=False,
        help="Whether to save the session data on every request")
    django.session_expire_at_browser_close = BoolConfigOption(default=False,
        help="Whether a user's session cookie expires when the Web browser "
             "is closed")
    django.session_engine = StringConfigOption(
        default='django.contrib.sessions.backends.db',
        help="The module to store session data")
    django.session_file_path = StringConfigOption(null=True,
        help="Directory to store session files if using the file session "
             "module. If None, the backend will use a sensible default")

    #########
    # CACHE #
    #########

    django.cache_backend = StringConfigOption(default='locmem://',
        help="The cache backend to use. See the docstring in "
             "django.core.cache for the possible values")
    django.cache_middleware_key_prefix = StringConfigOption(default='')
    django.cache_middleware_seconds = IntConfigOption(default=600)

    ####################
    # COMMENTS         #
    ####################

    django.comments_allow_profanities = BoolConfigOption(default=False)
    django.profanities_list = LinesConfigOption(item=StringConfigOption(),
        default=['asshat', 'asshead', 'asshole', 'cunt', 'fuck', 'gook',
                 'nigger', 'shit'],
        help="The profanities that will trigger a validation error in the "
             "'hasNoProfanities' validator. All of these should be in "
             "lowercase")
    django.comments_banned_users_group = StringConfigOption(null=True,
        help="The group ID that designates which users are banned. "
             "Set to None if you're not using it")
    django.comments_moderators_group = StringConfigOption(null=True,
        help="The group ID that designates which users can moderate comments. "
             "Set to None if you're not using it")
    django.comments_sketchy_users_group = StringConfigOption(null=True,
        help="The group ID that designates the users whose comments should be "
             "e-mailed to MANAGERS. Set to None if you're not using it")
    django.comments_first_few = IntConfigOption(default=0,
        help="The system will e-mail MANAGERS the first COMMENTS_FIRST_FEW "
             "comments by each user. Set this to 0 if you want to disable it")
    django.banned_ips = TupleConfigOption(
        help="A tuple of IP addresses that have been banned from "
             "participating in various Django-powered features")

    ##################
    # AUTHENTICATION #
    ##################

    django.authentication_backends = LinesConfigOption(
        item=StringConfigOption(),
        default=['django.contrib.auth.backends.ModelBackend'])
    django.login_url = StringConfigOption(default='/accounts/login/')
    django.logout_url = StringConfigOption(default='/accounts/logout/')
    django.login_redirect_url = StringConfigOption(default='/accounts/profile/')
    django.password_reset_timeout_days = IntConfigOption(default=3,
        help="The number of days a password reset link is valid for")

    ###########
    # TESTING #
    ###########

    django.test_runner = StringConfigOption(
        default='django.test.simple.run_tests',
        help="The name of the method to use to invoke the test suite")
    django.test_database_name = StringConfigOption(null=True,
        help="The name of the database to use for testing purposes. "
             "If None, a name of 'test_' + DATABASE_NAME will be assumed")
    django.test_database_charset = StringConfigOption(null=True,
        help="Strings used to set the character set and collation order for "
             "the test database. These values are passed literally to the "
             "server, so they are backend-dependent. If None, no special "
             "settings are sent (system defaults are used)")
    django.test_database_collation = StringConfigOption(null=True,
        help="Strings used to set the character set and collation order for "
             "the test database. These values are passed literally to the "
             "server, so they are backend-dependent. If None, no special "
             "settings are sent (system defaults are used)")

    ############
    # FIXTURES #
    ############

    django.fixture_dirs = LinesConfigOption(item=StringConfigOption(),
        help="The list of directories to search for fixtures")

    ####################
    # PROJECT TEMPLATE #
    ####################

    django.site_id = IntConfigOption(default=1)
    django.root_urlconf = StringConfigOption(default='urls')


class Django112Schema(BaseDjangoSchema):
    version = '1.1.2'

    # sections
    django = deepcopy(BaseDjangoSchema.django)

    ################
    # CORE         #
    ################

    # update default value
    django.languages.default = (
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
    )


class Django125Schema(Django112Schema):
    version = '1.2.5'

    # sections
    django = deepcopy(Django112Schema.django)

    ################
    # CORE         #
    ################

    # update default value
    django.languages.default = [
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
    ]

    django.use_l10n = BoolConfigOption(
        default=True,
        help="If you set this to False, Django will not format dates, "
            "numbers and calendars according to the current locale")

    django.databases = DictConfigOption(
        item=UpperCaseDictConfigOption(spec={
            'engine': StringConfigOption(default='django.db.backends.'),
            'name': StringConfigOption(),
            'user': StringConfigOption(),
            'password': StringConfigOption(),
            'host': StringConfigOption(),
            'port': StringConfigOption(),
        }),
        default={
            'default': {
                'engine': 'django.db.backends.',
                'name': '',
                'user': '',
                'password': '',
                'host': '',
                'port': '',
            }
        })
    django.database_routers = LinesConfigOption(
        item=StringConfigOption(),
        help="Classes used to implement db routing behaviour")

    django.email_backend = StringConfigOption(
        default='django.core.mail.backends.smtp.EmailBackend',
        help="The email backend to use. For possible shortcuts see "
            "django.core.mail. The default is to use the SMTP backend. "
            "Third party backends can be specified by providing a Python "
            "path to a module that defines an EmailBackend class.")

    django.installed_apps.default = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
    ]

    django.template_loaders.default = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]

    django.template_context_processors.default = [
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.contrib.messages.context_processors.messages',
    ]

    django.format_module_path = StringConfigOption(
        null=True, default=None,
        help="Python module path where user will place custom format "
            "definition. The directory where this setting is pointing "
            "should contain subdirectories named as the locales, "
            "containing a formats.py file")
    django.short_date_format = StringConfigOption(
        default='m/d/Y',
        help="Default short formatting for date objects")
    django.short_datetime_format = StringConfigOption(
        default='m/d/Y P',
        help="Default short formatting for datetime objects")
    django.date_input_formats = LinesConfigOption(
        item=StringConfigOption(),
        default=[
            '%%Y-%%m-%%d', '%%m/%%d/%%Y', '%%m/%%d/%%y', # '2006-10-25', '10/25/2006', '10/25/06'
            '%%b %%d %%Y', '%%b %%d, %%Y',               # 'Oct 25 2006', 'Oct 25, 2006'
            '%%d %%b %%Y', '%%d %%b, %%Y',               # '25 Oct 2006', '25 Oct, 2006'
            '%%B %%d %%Y', '%%B %%d, %%Y',               # 'October 25 2006', 'October 25, 2006'
            '%%d %%B %%Y', '%%d %%B, %%Y',               # '25 October 2006', '25 October, 2006'
        ],
        help="Default formats to be used when parsing dates from input "
            "boxes, in order")
    django.time_input_formats = LinesConfigOption(
        item=StringConfigOption(),
        default=[
            '%%H:%%M:%%S',     # '14:30:59'
            '%%H:%%M',         # '14:30'
        ],
        help="Default formats to be used when parsing times from input "
            "boxes, in order")
    django.datetime_input_formats = LinesConfigOption(
        item=StringConfigOption(),
        default=[
            '%%Y-%%m-%%d %%H:%%M:%%S',     # '2006-10-25 14:30:59'
            '%%Y-%%m-%%d %%H:%%M',         # '2006-10-25 14:30'
            '%%Y-%%m-%%d',                 # '2006-10-25'
            '%%m/%%d/%%Y %%H:%%M:%%S',     # '10/25/2006 14:30:59'
            '%%m/%%d/%%Y %%H:%%M',         # '10/25/2006 14:30'
            '%%m/%%d/%%Y',                 # '10/25/2006'
            '%%m/%%d/%%y %%H:%%M:%%S',     # '10/25/06 14:30:59'
            '%%m/%%d/%%y %%H:%%M',         # '10/25/06 14:30'
            '%%m/%%d/%%y',                 # '10/25/06'
        ],
        help="Default formats to be used when parsing dates and times "
            "from input boxes, in order")

    django.first_day_of_week = IntConfigOption(
        default=0,
        help="First day of week, to be used on calendars. 0 means Sunday, "
            "1 means Monday...")
    django.decimal_separator = StringConfigOption(
        default='.',
        help="Decimal separator symbol")
    django.use_thousand_separator = BoolConfigOption(
        default=False,
        help="Boolean that sets whether to add thousand separator when "
            "formatting numbers")
    django.number_grouping = IntConfigOption(
        default=0,
        help="Number of digits that will be together, when splitting them "
            "by THOUSAND_SEPARATOR. 0 means no grouping, 3 means "
            "splitting by thousands...")
    django.thousand_separator = StringConfigOption(
        default=',',
        help="Thousand separator symbol")

    ##############
    # MIDDLEWARE #
    ##############

    django.middleware_classes.default = [
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]

    ########
    # CSRF #
    ########

    django.csrf_failure_view = StringConfigOption(
        default='django.views.csrf.csrf_failure',
        help="Dotted path to callable to be used as view when a request "
            "is rejected by the CSRF middleware")
    django.csrf_cookie_name = StringConfigOption(
        default='csrftoken',
        help="Name for CSRF cookie")
    django.csrf_cookie_domain = StringConfigOption(
        null=True,
        help="Domain for CSRF cookie")

    ############
    # MESSAGES #
    ############

    django.message_storage = StringConfigOption(
        default='django.contrib.messages.storage.user_messages.'
            'LegacyFallbackStorage',
        help="Class to be used as messages backend")

    ###########
    # TESTING #
    ###########

    django.test_runner.default = (
        'django.test.simple.DjangoTestSuiteRunner')
    django.test_runner.help = (
        "The name of the class to use to run the test suite")


class Django13Schema(Django125Schema):
    version = '1.3'

    # sections
    django = deepcopy(Django125Schema.django)

    ################
    # CORE         #
    ################

    # update default value
    django.languages.default = [
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
    ]

    django.template_context_processors.default = [
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.debug',
        'django.core.context_processors.i18n',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'django.contrib.messages.context_processors.messages',
    ]

    django.static_root = StringConfigOption(
        default='',
        help='Absolute path to the directory that holds static files.')

    django.static_url = StringConfigOption(
        null=True, default=None,
        help='URL that handles the static files served from STATIC_ROOT.')

    ############
    # SESSIONS #
    ############

    django.session_cookie_httponly = BoolConfigOption(
        default=False,
        help='Whether to use the non-RFC standard htt pOnly flag (IE, FF3+, others)')

    #########
    # CACHE #
    #########

    # remove obsoleted setting
    del django.cache_backend

    django.caches = DictConfigOption()
    django.cache_middleware_alias = StringConfigOption(default='default')

    ############
    # COMMENTS #
    ############

    django.profanities_list.default = ()

    ###########
    # LOGGING #
    ###########

    django.logging_config = StringConfigOption(
        default='django.utils.log.dictConfig',
        help='The callable to use to configure logging')
    django.logging = DictConfigOption(
        spec={
            'version': IntConfigOption(default=1),
            'disable_existing_loggers': BoolConfigOption(default=False),
            'handlers': DictConfigOption(
                spec={
                    'mail_admins': DictConfigOption(
                        spec={
                            'level': StringConfigOption(default='ERROR'),
                            'class': StringConfigOption(
                                default='django.utils.log.AdminEmailHandler'),
                        }),
                }),
            'loggers': DictConfigOption(
                spec={
                    'django.request': DictConfigOption(
                        spec={
                            'handlers': LinesConfigOption(
                                item=StringConfigOption(),
                                default=['mail_admins']),
                            'level': StringConfigOption(default='ERROR'),
                            'propagate': BoolConfigOption(default=True),
                        }),
                }),
        },
        help='The default logging configuration. This sends an email to the '
            'site admins on every HTTP 500 error. All other records are sent '
            'to the bit bucket.')

    ###############
    # STATICFILES #
    ###############

    django.staticfiles_dirs = LinesConfigOption(
        item=StringConfigOption(),
        help='A list of locations of additional static files')
    django.staticfiles_storage = StringConfigOption(
        default='django.contrib.staticfiles.storage.StaticFilesStorage',
        help='The default file storage backend used during the build process')
    django.staticfiles_finders = LinesConfigOption(
        item=StringConfigOption(),
        default=[
            'django.contrib.staticfiles.finders.FileSystemFinder',
            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        ],
        help='List of finder classes that know how to find static files in '
            'various locations.')

    django.admin_media_prefix.default = '/static/admin/'


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
        if version not in self._schemas:
            msg = "No schema registered for version %r" % version
            if strict:
                raise ValueError(msg)
            else:
                logging.warn(msg)

            versions = sorted(self._schemas.keys())
            if not versions:
                raise ValueError("No schemas registered")

            last = versions[0]
            for v in sorted(self._schemas.keys()):
                if version < v:
                    break
                last = v
            version = last
            logging.warn("Falling back to schema for version %r" % version)
        return self._schemas[version]


schemas = DjangoSchemaFactory()
schemas.register(BaseDjangoSchema, '1.0.2 final')
schemas.register(BaseDjangoSchema, '1.0.4')
schemas.register(Django112Schema)
schemas.register(Django112Schema, '1.1.4')
schemas.register(Django125Schema)
schemas.register(Django13Schema)
