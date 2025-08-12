from django.http import HttpResponse
from django.template.loader import render_to_string

from apps.blog.views.resume.base import ResumePreviewBaseView
from apps.blog.context.global_context import shared


class ResumeDownloadView(ResumePreviewBaseView):
    template_name = "blog/resume/preview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(shared(self.request))
        return context

    def get(self, request, *args, **kwargs):
        # WeasyPrint is only used in PDF generation and requires heavy system dependencies
        # (Cairo, Pango, etc.) that are not installed in local dev environments.
        # To avoid breaking commands like `makemigrations` locally, we import it lazily
        # inside the function where it’s needed. This ensures Docker/prod environments
        # still have full PDF functionality without forcing all developers to install
        # the extra dependencies locally.
        from weasyprint import HTML

        # 1. Render template to HTML string
        html_string = render_to_string(
            self.template_name, context=self.get_context_data()
        )

        # 2. Create PDF in memory
        pdf_file = HTML(
            string=html_string, base_url=request.build_absolute_uri()
        ).write_pdf()

        # 3. Return as downloadable file
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            'inline; filename="nguyen_tran_quang_trung.pdf"'
        )
        return response
