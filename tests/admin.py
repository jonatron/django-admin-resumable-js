from django.contrib import admin
from .models import Foo


class FooAdmin(admin.ModelAdmin):
    pass


admin.site.register(Foo, FooAdmin)
