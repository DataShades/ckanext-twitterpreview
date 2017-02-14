import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan import plugins as p
import ckan.logic as logic

from pylons import config

ignore_empty = p.toolkit.get_validator('ignore_empty')
DEFAULT_TWIITER_FORMATS = ['TWITTER FEED']


def twitter_feed_validation(resource):
    if resource['format'].upper() in DEFAULT_TWIITER_FORMATS:
        resource['format'] = resource['format'].upper()
        if not resource['url'].startswith('https://twitter.com'):
            if resource['url'].startswith('twitter.com'):
                resource['url'] = 'https://' + resource['url']
            else:
                message = [
                    (
                        'This Url is wrong for this resource format.'
                        ' The Url should match the example: '
                        "https://twitter.com/USERNAME"
                    )]
                raise logic.ValidationError({"Twitter": message})


class Twitter_FeedsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # IResourceController

    def before_create(self, context, resource):
        twitter_feed_validation(resource)

    def before_update(self, context, current, resource):
        twitter_feed_validation(resource)

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'twitter_feed_validation': twitter_feed_validation
        }

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'twitter_feeds')

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
        return (data_dict['resource'].get('format', '').upper()
                in DEFAULT_TWIITER_FORMATS)

    def view_template(self, context, data_dict):
        if data_dict['resource']['format'].upper() in DEFAULT_TWIITER_FORMATS:
            replies = toolkit.asbool(
                config.get('ckan.twitter.exclude_replies', False))
            data_dict['resource']['count_tweets'] = config.get(
                'ckan.twitter.max_feeds_count')
            user_screen_name = data_dict['resource'][
                'url'].rsplit('twitter.com/', 1)[1]
            data_dict['resource']['user_screen_name'] = user_screen_name
            data_dict['resource']['tweet_replies'] = replies
        return 'twitter_feed_view.html'

    def form_template(self, context, data_dict):
        return 'twitter_feed_from.html'
