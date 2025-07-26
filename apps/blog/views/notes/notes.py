from django.views.generic import ListView
from django.db.models import Count
from collections import defaultdict

from apps.blog.models import NotesToSelf


class NoteListView(ListView):
    model: NotesToSelf = NotesToSelf
    template_name = "blog/notes/index.html"
    context_object_name = "notes"

    def get_queryset(self):
        year = (
            self.model.published.values("year")
            .annotate(year_count=Count("id"))
            .order_by("-year")
        )
        posts = self.model.published.order_by("-year", "-created")

        default = defaultdict(list)
        for post in posts:
            default[post.year].append(post)

        queryset = []
        for year_item in year:
            year_value = year_item["year"]
            year_count = year_item["year_count"]
            queryset.append(
                {
                    "year": year_value,
                    "year_count": year_count,
                    "note_posts": default[year_value],
                }
            )

        return queryset

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
