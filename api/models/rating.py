from django.db import models

from api.models import User
from api.models.submission import Question


class Rating(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    review = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(choices=((1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')))

    class Meta:
        db_table = 'rating'
        unique_together = ('question', 'user')
        