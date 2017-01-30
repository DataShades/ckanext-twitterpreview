import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan import plugins as p
from pylons import config

import twitter
from datetime import datetime
ignore_empty = p.toolkit.get_validator('ignore_empty')
DEFAULT_TWIITER_FORMATS = ['twitter feed']


def twitter_feed_date(feed_date):
    date = datetime.strptime(
        feed_date, "%a %b %d %H:%M:%S +0000 %Y").strftime('%b %d')
    return date


class Twitter_FeedsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    def get_helpers(self):
        return {'twitter_feed_date': twitter_feed_date}

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'twitter_feeds')

    # IResourceController

    def before_show(self, resource_dict):
        return resource_dict

    # IResourceView

    def info(self):
        return {'name': 'twitter_feed_view',
                'title': p.toolkit._('Twitter feeds'),
                'icon': 'picture',
                'schema': {'twitter_url': [ignore_empty, unicode]},
                'iframed': False,
                'always_available': False,
                'default_title': p.toolkit._('Twitter feeds'),
                }

    def can_view(self, data_dict):
        return (data_dict['resource'].get('format', '').lower()
                in DEFAULT_TWIITER_FORMATS)

    def view_template(self, context, data_dict):
        if data_dict['resource']['format'].lower() in DEFAULT_TWIITER_FORMATS:
            feeds = []
            screen_name = data_dict['resource']['url'].split('/')
            api = twitter.api.Api(
                consumer_key=config.get('ckan.twitter.consumer_key'),
                consumer_secret=config.get('ckan.twitter.consumer_secret'),
                access_token_key=config.get('ckan.twitter.access_token_key'),
                access_token_secret=config.get('ckan.twitter.access_token_secret'))

            twitter_info = api.GetUserTimeline(
                screen_name=screen_name[3],
                count=config.get('ckan.twitter.max_feeds_count'))
            for feed in twitter_info:
                feed = {
                    'id': feed.retweeted_status.id if feed.retweeted_status else feed.id,
                    'created_at': feed.created_at,
                    'retweet_count': feed.retweet_count,
                    'text': feed.retweeted_status.text if feed.retweeted_status else feed.text,
                    'user': {
                        'id': feed.retweeted_status.user.id if feed.retweeted_status else feed.user.id,
                        'created_at': feed.retweeted_status.user.created_at if feed.retweeted_status else feed.user.created_at,
                        'description': feed.retweeted_status.user.description if feed.retweeted_status else feed.user.description,
                        'name': feed.retweeted_status.user.name if feed.retweeted_status else feed.user.name,
                        'profile_image_url': feed.retweeted_status.user.profile_image_url if feed.retweeted_status else feed.user.profile_image_url,
                        'screen_name': feed.retweeted_status.user.screen_name if feed.retweeted_status else feed.user.screen_name,
                        'statuses_count': feed.retweeted_status.user.statuses_count if feed.retweeted_status else feed.user.statuses_count
                    }
                }
                feeds.append(feed)

            data_dict['resource']['twitt_feeds_count'] = len(twitter_info)
            data_dict['resource']['twitt_feeds'] = feeds

        return 'twitter_feed_view.html'

    def form_template(self, context, data_dict):
        return 'twitter_feed_from.html'
