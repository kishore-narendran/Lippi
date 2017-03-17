from django.conf import settings
from django.db import models
from django.apps import apps

settings.configure(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cs221',
        'USER': 'kishore',
        'PASSWORD': 'chop1109',
        'HOST': 'localhost',
        'PORT': '5432',
    }
})


apps.populate((__name__,))


class LibModel(models.Model):
    class Meta:
        abstract = True
        app_label = __name__


class Document(LibModel):
    class Meta(LibModel.Meta):
        db_table = "documents"
    doc = models.TextField(primary_key=True, null=False)
    url = models.TextField(null=False)


class Term(LibModel):
    class Meta(LibModel.Meta):
        db_table = "terms"
    term = models.TextField(null=False, db_index=True)
    doc = models.ForeignKey(Document, null=False, db_column='doc')
    tag_type = models.CharField(null=False, max_length=6)
    position = models.IntegerField(null=False)

