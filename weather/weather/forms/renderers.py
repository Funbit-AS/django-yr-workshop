from django.forms.renderers import TemplatesSetting


class TailwindRenderer(TemplatesSetting):
    # Use an App Dir because DjangoTemplates doesn't look in DIRS list.
    form_template_name = "forecast/form.html"
