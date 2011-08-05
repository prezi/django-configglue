django-configglue 101
=====================

This is a minimalistic step-by-step guide on how to start using
django-configglue to manage the settings for your Django project.

Create the schema
-----------------

First we need to create the schema that will define the settings we want to
support in our configuration files.

Start by creating a module called *schema.py*, such as ::

    import django
    from configglue import schema
    from django_configglue.schema import schemas


    DjangoSchema = schemas.get(django.get_version())

    class MySchema(DjangoSchema):
        foo = schema.IntOption()
        bar = schema.BoolOption()

The `MySchema` schema will support all Django supported settings (as defined
in the `DjangoSchema` schema), and it introduces two custom options (`foo` and
`bar` in the default section -- `__main__`).

Create the config files
-----------------------

Now we need to create the configuration file where we specify the values we
want to have for our options. Create a file called *main.cfg* ::

    [__main__]
    foo = 1
    bar = true

    [django]
    database_engine = sqlite3
    database_name = :memory:
    installed_apps =
        django.contrib.auth
        django.contrib.contenttypes
        django.contrib.sessions
        django.contrib.sites
        django_configglue

Glue into django
----------------

Finally, we need to implement the glue between configglue and Django, so that
it can read out the settings defined in our configuration files.

Replace the standard *settings.py* module in your project with ::

    from django_configglue.utils import configglue
    from .schema import MySchema

    # make django aware of configglue-based configuration
    configglue(MySchema, ['main.cfg'], __name__)

Test
----

And let's make sure everything works as expected ::

    $ python manage.py settings --validate
    Settings appear to be fine.

Profit!
-------

That's it! Your project now uses django-configglue to manage it's
configuration. Congratulations!

If you want to know more about django-configglue, read
:ref:`walkthrough`.
