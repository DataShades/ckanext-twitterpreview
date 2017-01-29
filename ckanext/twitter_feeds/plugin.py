import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan import plugins as p
from pylons import config

import twitter

ignore_empty = p.toolkit.get_validator('ignore_empty')
DEFAULT_IMAGE_FORMATS = ['twitt']


class Twitter_FeedsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'twitter_feeds')

    # IResourceController

    def before_show(self, resource_dict):
        if resource_dict['format'] == 'twitt':
            feeds = []
            screen_name = resource_dict['url'].split('/')
            api = twitter.api.Api(
                consumer_key=config.get('ckan.twitter.consumer_key'),
                consumer_secret=config.get('ckan.twitter.consumer_secret'),
                access_token_key=config.get('ckan.twitter.access_token_key'),
                access_token_secret=config.get('ckan.twitter.access_token_secret'))

            twitter_info = api.GetUserTimeline(screen_name=screen_name[3], count=10)

            for feed in twitter_info:
                feed = {
                    'created_at': feed.created_at,
                    'retweet_count': feed.retweet_count,
                    'text': feed.text,
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
            resource_dict['twitt_feeds'] = feeds
        return resource_dict

    # IResourceView

    def info(self):
        return {'name': 'twitt',
                'title': p.toolkit._('Twitt'),
                'icon': 'picture',
                'schema': {'twitter_url': [ignore_empty, unicode]},
                'iframed': False,
                'always_available': False,
                'default_title': p.toolkit._('Twitt'),
                }

    def can_view(self, data_dict):
        return (data_dict['resource'].get('format', '').lower()
                in DEFAULT_IMAGE_FORMATS)

    def view_template(self, context, data_dict):
        return 'twitter_feed_view.html'

    def form_template(self, context, data_dict):
        return 'twitter_feed_from.html'
