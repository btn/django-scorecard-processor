from settings import *
from bundle_config import config

ADMIN_MEDIA_PREFIX = "/static/grappelli/"

CACHES = {
  'default': {
    'BACKEND': 'redis_cache.RedisCache',
    'LOCATION': '%s:%s' % (config['redis']['host'], config['redis']['port']),
    'OPTIONS': {
      'DB': 1,
      'PASSWORD': config['redis']['password'],
      'PARSER_CLASS': 'redis.connection.PythonParser'
    },
  },
}
CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'moz2012@ihpresults.net'
EMAIL_HOST_PASSWORD = 'd0c3251252aa3ba6a806464d2de418b2'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

SERVER_EMAIL='"Mozambique Survey 2012" <moz2012@ihpresults.net>'
DEFAULT_FROM_EMAIL=SERVER_EMAIL
ADMINS = (
    ('Sysadmin','sysadmin@ihpresults.net'),
)
MANAGERS = ADMINS
EMAIL_SUBJECT_PREFIX='[Production] '

