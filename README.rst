ckanext-twitter_feeds
=============


Installing
----------

To install the extension::

    $ git clone git@git.links.com.au:yrudenko/ckanext-twitter_feeds.git
    $ . /usr/lib/ckan/default/bin/activate
    $ python setup.py develop
    $ pip install -r requirements.txt

To activate it::

    Add it to the ckan.plugins in config file: ckan.plugins = twitter_feeds

    Add to the default_views field in config file: ckan.views.default_views = twitter_feed_view

    Add settings to config:

      ckan.twitter.consumer_key = your_consumer_key
      ckan.twitter.consumer_secret = your_consumer_secret
      ckan.twitter.access_token_key = your_access_token_key
      ckan.twitter.access_token_secret = your_access_token_secret
      ckan.twitter.max_feeds_count = 10 (The number is tweets you want to display, max 200)
      ckan.twitter.include_retweets= True (If you want to exclude retweets change from True to False)
      ckan.twitter.exclude_replies = False (If you want to exclude retweets change from False to True)

To generate your keys, first signup at https://twitter.com/signup and create your App at https://apps.twitter.com/. Click the “Create New App” button and fill out the fields.
After creating App you will see the App information. Click on the “Keys and Access Tokens” tab on the top there, generate all needed keys and copy them to your config file.


Creating resource
-----------------

To create a twitter resource, at the resource create form enter ```Twitter Feed``` at Format field and ```https://twitter.com/USERNAME``` at URL field, where USERNAME is name of the person or group you want to get infromation from, for exmaple: https://twitter.com/ckanproject


Testing
-------

Proceed with the instructions at http://docs.ckan.org/en/latest/contributing/test.html in Set up the test databases section.

After creating Test Databases, at CKAN test-core.ini file::
    
    Change the password for `sqlalchemy.url` field to connect the DB while testing.

Add in test.ini file (file in extension)::

    ckan.twitter.consumer_key = your_consumer_key
    ckan.twitter.consumer_secret = your_consumer_secret
    ckan.twitter.access_token_key = your_access_token_key
    ckan.twitter.access_token_secret = your_access_token_secret
    ckan.twitter.max_feeds_count = 10 (The number is tweets you want to display, max 200)

    Set the right use = config:/usr/lib/ckan/default/src/ckan/test-core.ini path to test-core.ini

Run the command from extension directory::

    nosetests --with-pylons=test.ini --nologcapture --rednose -s -x -v --reset-db