import datetime


def get_year(date):
    first_day = datetime.date(date.year, 1, 1)
    last_day = datetime.date(date.year, 12, 31)
    return first_day, last_day


def get_query_params(request, self):
    year_input = request.GET.get('year')
    if year_input is None:
        year_datetime = datetime.datetime.now()
    else:
        year_datetime = datetime.datetime(int(year_input), 1, 1)
    start_date, end_date = get_year(year_datetime)
    return start_date, end_date, year_datetime
