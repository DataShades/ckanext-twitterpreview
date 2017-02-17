# CKAN modules
import ckan.tests.factories as factories
from ckan.tests.helpers import (
    FunctionalTestBase,
    _get_test_app
)
from ckan.tests.legacy.pylons_controller import PylonsTestCase
import ckan.tests.legacy as tests
import ckan.plugins.toolkit as tk

# Nosetests module
import nose.tools as nt

call_api = tests.call_action_api

PylonsTestCase()


class TestTwitterFeeds(PylonsTestCase, FunctionalTestBase):

    def setup(self):
        super(TestTwitterFeeds, self).setup()

        self.app = _get_test_app()

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
            url='notmatchingtwitterurl.com',
            format='twitter feed')

    def test_view_created(self):
        dataset = factories.Dataset(
            private=False)
        resource = factories.Resource(
            url='https://twitter.com/ckanproject',
            format='twitter feed',
            name='Twitter Feed',
            package_id=dataset['id'])
        pagec = self.app.get(
            '/dataset/' + dataset['name'] + '/resource/' + resource['id'])
        tweet_created = pagec.html.select(
            '.resource-view .m-top.ckanext-datapreview')
        print tweet_created
        nt.assert_true(tweet_created)
