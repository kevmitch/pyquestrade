import questrade.base
import datetime
import pytz

startofday = datetime.time.min
endofday = datetime.time.max

def partition_datetime(start, end):
    """
    Partition the date range into non-overlapping intervals of 31 days.

    The intervals do not overlap, even at the join points. The start of one
    interval should be one microsecond (python datetime resolution) later than
    the end of the previous. This is necessary to avoid duplicate dates since
    the Questrade API returns results including both endpoints.

    Accepts datetime and date objects. If date objects are passed, they are
    converted to datetime objects internally. The time of start is set to
    midnight, while that of end is set to one microsecond to midnight.

    If you pass datetime objects, then their time is untouched. In particular if
    you pass a datetime with a time of midnight as end, only the first
    microsecond of that day will be included in the final
    interval. Normally, this might be allright since it seems that Questrade
    considers everything to happen at midnight of the day it actually occured.

    This horrible mess is necessary because Questrade refuses to service
    requests for more than 31 days of history.
    """
    if not hasattr(start, 'time'):
        start = datetime.datetime.combine(start, startofday)
    if not hasattr(end, 'time'):
        end = datetime.datetime.combine(end, endofday)

    current = start
    interval = datetime.timedelta(days=31)
    open_interval = interval - datetime.datetime.resolution
    stop = end - open_interval
    while start < stop:
        current = start + open_interval
        yield start, current
        start = start + interval

    yield start, end

class Account(questrade.base.ApiABC):
    """
    Represents a single Questrade account.

    Initialize with a questrade.Auth instance and account parameter kwargs,
    which become instance variables. Parameters are documented at

    account-calls/accounts
    """

    def __init__(self, auth, **kwargs):
        self.__dict__.update(kwargs)
        super(Account, self).__init__(auth)

    def __str__(self):
        return "%s: %s" % (self.type, self.number)

    def __repr__(self):
        return "<Account %s>" % (self)

    def url(self, operation):
        """
        Construct the URL for the current account and provided operation.
        """
        operation = 'accounts/%s/%s' % (self.number, operation)
        return super(Account, self).url(operation)

    def positions(self):
        """
        Retrieve positions in a specified account.

        account-calls/accounts-id-positions
        """
        return self.get('positions')['positions']

    def balances(self):
        """
        Retrieve per-currency and combined balances for a specified account.

        account-calls/accounts-id-balances
        """
        return self.get('balances')

    def executions(self):
        """
        Retrieve executions for a specific account.

        account-calls/accounts-id-executions
        """
        return self.get('executions')['executions']

    def orders(self):
        """
        Retrieve orders for specified account.

        account-calls/accounts-id-orders
        """
        return self.get('orders')['orders']

    def _activities(self, start, end):
        """
        Retrieve account activities.

        Only date ranges spanning 31 days or less are allowed.
        """
        def _format_datetime(dt):
            """Return an ISO 8601 string with one second resolution."""
            if not dt.tzinfo:
                dt = pytz.timezone('America/Toronto').localize(dt)

            # Questrade API doesn't support microseconds.
            return dt.replace(microsecond=0).isoformat()

        params = {
            'startTime': _format_datetime(start),
            'endTime': _format_datetime(end)
        }
        return self.get('activities', params)['activities']

    def activities(self, start, end):
        """
        Retrieve account activities.

        Takes start and end datetime datetime objects as arguments. If they
        don't have tzinfo set, they will be localize()ed to America/Toronto.

        This includes cash transactions, dividends, trades, etc.

        This method works around the Questrade API limitation of 31 days per
        query by breaking up large queries into multiple calls. As a result,
        requesting large blocks of time may take a while.

        account-calls/accounts-id-activities
        """
        activities = []
        for s, e in partition_datetime(start, end):
            activities.extend(self._activities(s, e))

        return activities
