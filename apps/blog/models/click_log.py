from django.db import models


class ClickLog(models.Model):
    """
    Track download clicks.
    """

    date = models.DateField(db_index=True)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Click Log"
        verbose_name_plural = "Click Logs"

    def __str__(self):
        return f"Count {self.count} at {self.date}"
