from django.contrib import admin


class PrismAdmin(admin.ModelAdmin):
    """
    Admin class for Prism syntax highlighting.
    This class is used to include Prism CSS and JS files in the admin interface.
    """

    class Media:
        css = {"all": ["prism/prism.css"]}
        js = ("prism/prism.js",)
