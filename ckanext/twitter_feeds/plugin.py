import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan import plugins as p
from pylons import config

import twitter
from datetime import datetime
import ckan.logic as logic

from ttp import ttp
p2 = ttp.Parser()

ignore_empty = p.toolkit.get_validator('ignore_empty')
DEFAULT_TWIITER_FORMATS = ['twitter feed']

twitter_api = twitter.api.Api(
    consumer_key=config.get('ckan.twitter.consumer_key'),
    consumer_secret=config.get('ckan.twitter.consumer_secret'),
    access_token_key=config.get('ckan.twitter.access_token_key'),
    access_token_secret=config.get('ckan.twitter.access_token_secret')
)


def twitter_feed_date(feed_date):
    date = datetime.strptime(
        feed_date, "%a %b %d %H:%M:%S +0000 %Y").strftime('%b %d')
    return date


def twitter_feed_validation(resource):
    screen_name = resource['url'].split('/')
    if resource['format'].lower() in DEFAULT_TWIITER_FORMATS:
        if not resource['url'].startswith('https://twitter.com'):
            message = ['This Url is wrong for this resource format. The Url should match for example: "https://twitter.com/USERNAME"']
            raise logic.ValidationError({"Twitter": message})
        try:
            test = twitter_api.GetUserTimeline(
                screen_name=screen_name[3],
                count=1)
        except twitter.TwitterError, e:
            for m in e.message:
                message = [m['message']]
                raise logic.ValidationError({"Twitter": message})


class Twitter_FeedsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    def before_create(self, context, resource):
        twitter_feed_validation(resource)

    def before_update(self, context, current, resource):
        twitter_feed_validation(resource)

    def get_helpers(self):
        return {
            'twitter_feed_date': twitter_feed_date,
            'twitter_feed_validation': twitter_feed_validation
        }

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
            twitter_info = twitter_api.GetUserTimeline(
                screen_name=screen_name[3],
                count=config.get('ckan.twitter.max_feeds_count'),
                include_rts=False)
            for feed in twitter_info:
                retweeted = False
                if feed.retweeted_status:
                    retweeted = True
                    text = feed.retweeted_status.text
                else:
                    text = feed.text

                if 'https://t.co/' in text:
                    last_url = text.rsplit('https://t.co/', 1)[1].split()
                    last_url = last_url[0]

                    if text.endswith(last_url):
                        last_url = 'https://t.co/' + last_url
                        text = text.replace(last_url, '')

                complete_text = p2.parse(text)
                feed = {
                    'id': feed.retweeted_status.id if feed.retweeted_status else feed.id,
                    'created_at': feed.created_at,
                    'retweet_count': feed.retweet_count,
                    'text': complete_text.html,
                    'user': {
                        'name': feed.user.name,
                        'id': feed.user.id
                    },
                    'twitt_info': {
                        'id': feed.retweeted_status.user.id if feed.retweeted_status else feed.user.id,
                        'created_at': feed.retweeted_status.user.created_at if feed.retweeted_status else feed.user.created_at,
                        'description': feed.retweeted_status.user.description if feed.retweeted_status else feed.user.description,
                        'name': feed.retweeted_status.user.name if feed.retweeted_status else feed.user.name,
                        'profile_image_url': feed.retweeted_status.user.profile_image_url if feed.retweeted_status else feed.user.profile_image_url,
                        'screen_name': feed.retweeted_status.user.screen_name if feed.retweeted_status else feed.user.screen_name,
                        'statuses_count': feed.retweeted_status.user.statuses_count if feed.retweeted_status else feed.user.statuses_count
                    },
                    'retweeted': retweeted
                }
                feeds.append(feed)

            data_dict['resource']['twitt_feeds_count'] = len(twitter_info)
            data_dict['resource']['twitt_feeds'] = feeds
        return 'twitter_feed_view.html'

    def form_template(self, context, data_dict):
        return 'twitter_feed_from.html'
