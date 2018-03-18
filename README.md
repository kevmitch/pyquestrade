# pyquestrade
This is a thin python wrapper around Questrade's REST API.

[Questrade](http://www.questrade.com/) is a Canadian discount broker. They
provide a [REST API](http://www.questrade.com/api) for use by clients and
developers.

This module provides python bindings. It strives to be as simple as possible so
that mere mortal users may read the code and convince themselves it's not going
to steal / lose all their cash or mine bitcoin. It does not attempt to include
any analysis, processing, recording or automation tools. These should be
developed separately.

Note that Questrade has or will soon remove the ability to execute trades using
its API due to regulatory concerns. This module was probably never going to
support that anyway because it's too scary.

## Getting started

To use it, you need an API key provided by Questrade. Go to the Questrade "App
Hub" page by accessing the drop down menu under your username within your
Questrade account, or go there directly by visiting
https://login.questrade.com/APIAccess/UserApps.aspx.

Select "Register Personal App" to add a new entry for pyquestrade. It requires
to following permissions:

* Retrieve balances, positions, orders and executions
* Retrieve delayed and real-time market data

Specifically, it does not require "Place, modify and cancel orders". There is
currently no need for a callback URL.

Once you've createed the new App, click the "New Device" button, and then
"Generate new token". Put the resulting string into the configuration file

    echo <token> > ~/.config/pyquestrade/refresh_token

Now you're ready to start using the python module.

    $ git clone https://github.com/kevmitch/pyquestrade.git
    $ cd pyquestrade
    $ ipython
    In [1]: import Api
    In [2]: api=Api()

Use the `api` object to query the list of your accounts

    In [3]: api.accounts()
    Out[3]:
    [{u'clientAccountType': u'Individual',
      u'isBilling': False,
      u'isPrimary': False,
      u'number': u'01234567',
      u'status': u'Active',
      u'type': u'Margin'},
     {u'clientAccountType': u'Individual',
      u'isBilling': False,
      u'isPrimary': False,
      u'number': u'89012345',
      u'status': u'Active',
      u'type': u'TFSA'},
     {u'clientAccountType': u'Individual',
      u'isBilling': True,
      u'isPrimary': True,
      u'number': u'67890123',
      u'status': u'Active',
      u'type': u'RRSP'}]

Get account activities for one of them

    In [4]: from datetime import date
    In [5]: account=api.get_account(type='TFSA')
    In [6]: account.activities(date(2018,2,7),date(2018,2,8))
    [{u'action': u'Buy',
      u'commission': -5.06,
      u'currency': u'CAD',
      u'description': u'VECIMA NETWORKS INC            WE ACTED AS AGENT              AVG PRICE - ASK US FOR DETAILS  ',
      u'grossAmount': -1236.1,
      u'netAmount': -1241.16,
      u'price': 9.508462,
      u'quantity': 130,
      u'settlementDate': u'2018-02-07T00:00:00.000000-05:00',
      u'symbol': u'VCM.TO',
      u'symbolId': 40517,
      u'tradeDate': u'2018-02-05T00:00:00.000000-05:00',
      u'transactionDate': u'2018-02-07T00:00:00.000000-05:00',
      u'type': u'Trades'},
     {u'action': u'Buy',
      u'commission': -5.16,
      u'currency': u'CAD',
      u'description': u'TORONTO-DOMINION BANK          WE ACTED AS AGENT                ',
      u'grossAmount': -4352.35,
      u'netAmount': -4357.51,
      u'price': 71.35,
      u'quantity': 61,
      u'settlementDate': u'2018-02-08T00:00:00.000000-05:00',
      u'symbol': u'TD.TO',
      u'symbolId': 38938,
      u'tradeDate': u'2018-02-06T00:00:00.000000-05:00',
      u'transactionDate': u'2018-02-08T00:00:00.000000-05:00',
      u'type': u'Trades'}]

Or list positions including cost basis and market value

    In [6]: account=api.positions()
    Out [6]:
    [{u'averageEntryPrice': 71.35,
      u'closedPnl': 0,
      u'closedQuantity': 0,
      u'currentMarketValue': 4631.12,
      u'currentPrice': 75.92,
      u'isRealTime': False,
      u'isUnderReorg': False,
      u'openPnl': 278.77,
      u'openQuantity': 61,
      u'symbol': u'TD.TO',
      u'symbolId': 38938,
      u'totalCost': 4352.35},
     {u'averageEntryPrice': 9.626604,
      u'closedPnl': 0,
      u'closedQuantity': 0,
      u'currentMarketValue': 4913.1,
      u'currentPrice': 9.27,
      u'isRealTime': False,
      u'isUnderReorg': False,
      u'openPnl': -189.00012,
      u'openQuantity': 530,
      u'symbol': u'VCM.TO',
      u'symbolId': 40517,
      u'totalCost': 5102.10012}]
