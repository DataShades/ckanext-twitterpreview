import ckan.tests.factories as factories
import nose.tools as nt
from functools import partial
from ckan.tests.helpers import (
    FunctionalTestBase,
    _get_test_app
)
import random
import string
from uuid import uuid4
from ckan.tests.legacy.pylons_controller import PylonsTestCase
import ckan.tests.helpers as helpers
import ckan.model as model
import ckan.tests.legacy as tests

import ckan.plugins.toolkit as tk
from pylons import config
import twitter

call_api = tests.call_action_api

PylonsTestCase()


class TestTwitterFeeds(PylonsTestCase, FunctionalTestBase):

    def setup(self):
        super(TestTwitterFeeds, self).setup()
        self.sysadmin = factories.Sysadmin()
        # self.user_member = factories.User()
        # self.user_editor = factories.User()
        # self.org = factories.Organization(users=[
        #     {'name': self.user_editor['name'], 'capacity': 'editor'},
        #     {'name': self.user_member['name'], 'capacity': 'member'}
        # ])
        # self.dataset = factories.Dataset()

        self.app = _get_test_app()

        self.twitter_api = twitter.api.Api(
            consumer_key=config.get('ckan.twitter.consumer_key'),
            consumer_secret=config.get('ckan.twitter.consumer_secret'),
            access_token_key=config.get('ckan.twitter.access_token_key'),
            access_token_secret=config.get('ckan.twitter.access_token_secret')
        )

    def test_check_authentication(self):
        # twitter_api = twitter.api.Api(
        #     consumer_key=config.get('ckan.twitter.consumer_key'),
        #     consumer_secret=config.get('ckan.twitter.consumer_secret'),
        #     access_token_key=config.get('ckan.twitter.access_token_key'),
        #     access_token_secret=config.get('ckan.twitter.access_token_secret')
        # )
        nt.assert_true(self.twitter_api.VerifyCredentials())

        twitter_api = twitter.api.Api(
            consumer_key=config.get('ckan.twitter.consumer_key'),
            consumer_secret=config.get('ckan.twitter.consumer_secret'),
            access_token_key=config.get('ckan.twitter.access_token_key'),
            access_token_secret='not_existing_key'
        )

        nt.assert_raises(
            twitter.TwitterError,
            twitter_api.VerifyCredentials)

    def test_resource_twitter_create(self):
        resource = factories.Resource(
            name='Twitter Feed',
            url='https://twitter.com/ckanproject',
            format='twitter feed'
        )
        nt.assert_true(resource)

        nt.assert_raises(
            tk.ValidationError,
            factories.Resource,
            url='https://twitter.com/somelongtextthatnotexists',
            format='twitter feed')

        nt.assert_raises(
            tk.ValidationError,
            factories.Resource,
            url='notmatchingtwitterurl.com',
            format='twitter feed')

    def test_resource_twitter_get_twitts(self):
        resource = factories.Resource(
            name='Twitter Feed',
            url='https://twitter.com/ckanproject',
            format='twitter feed',
            can_be_previewed=False,
            has_views=True
        )
        screen_name = resource['url'].split('/')
        twitter_info = self.twitter_api.GetUserTimeline(
            screen_name=screen_name[3],
            count=config.get('ckan.twitter.max_feeds_count'))

        nt.assert_true(twitter_info)

        nt.assert_raises(
            twitter.TwitterError,
            self.twitter_api.GetUserTimeline,
            screen_name='somelongtextthatnotexists',
            count=config.get('ckan.twitter.max_feeds_count'))
