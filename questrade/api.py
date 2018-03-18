from questrade import base, accounts

class Api(base.ApiABC):
    """
    User entry point for the Questrade API.

    Initialize with a questrade.Auth instance. If none is provided, one will be
    created with the default parameters.

    An instance of this class can be used to make authorized Questrade api
    calls.

    Each operation cites it's Questrade API documentation page relative to

    http://www.questrade.com/api/documentation/rest-operations/
    """

    def time(self):
        """
        Retrieves current server time.

        account-calls/time
        """
        return self.get('time')['time']

    def userId(self):
        """
        Internal identifier of the authorized user.

        account-calls/accounts
        """
        return self.get('accounts')['userId']

    def accounts(self):
        """
        Retrieves the accounts associated with the authorized user.

        The user is internally identified by the userId() method.

        This method returns a list of dictionaries containing information about
        each account.

        account-calls/accounts
        """
        return self.get('accounts')['accounts']

    def get_account(self, **kwargs):
        """
        Retrieve a questrade.Account object for the first matching account.

        kwargs must be a subset of account parameters returned by accounts() as
        documeneted at

        account-calls/accounts
        """
        for account_dict in self.accounts():
            if set(kwargs.items()).issubset(account_dict.items()):
                return accounts.Account(self.auth, **account_dict)

    def get_accounts(self):
        """
        Retrieves questrade.Account objects for all accesible accounts.
        """
        return (accounts.Account(self.auth, **account_dict)
                for account_dict in self.accounts())
