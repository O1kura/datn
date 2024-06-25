import datetime

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.models import User
from api.models.submission import Submission, File
from api.utils.dashboard_utils import get_query_params
import pytz


class SubmissionByMonthView(GenericAPIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        utc_time = pytz.utc

        start_date, end_date, year_datetime = get_query_params(request, self)
        submissions_month = Submission.objects.filter(created_at__gte=start_date,
                                                      created_at__lte=end_date,
                                                      deleted_at__isnull=True).annotate(
            month=TruncMonth('created_at')).values('month') \
            .annotate(total=Count('id'), total_file_count=Sum('file_count'))

        file_month = File.objects.filter(created_at__gte=start_date,
                                         created_at__lte=end_date,
                                         deleted_at__isnull=True).annotate(
            month=TruncMonth('submission__created_at')).values('month').annotate(total=Count('id'))

        result = {}
        for i in range(1, 13):
            result[i] = {'month': utc_time.localize(datetime.datetime(year_datetime.year, i, 1)),
                         'total_submission': 0,
                         'file_sent': 0,
                         'total_file': 0}

        for i in submissions_month:
            result[i["month"].month] = {"month": i["month"], "total_submission": i["total"],
                                        'file_sent': i["total_file_count"]}

        for i in file_month:
            result[i["month"].month]['total_file'] = i["total"]

        return Response(result)


class UsersCountView(GenericAPIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        res = User.objects.all().values('is_superuser').annotate(total=Count('id'))

        return Response(res)
