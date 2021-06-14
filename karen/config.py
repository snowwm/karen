import os
import logging

import karen

LOGLEVEL = logging.WARNING

if os.getenv('DEBUG'):
    LOGLEVEL = logging.DEBUG

if os.getenv('LOGLEVEL'):
    level = getattr(logging, os.getenv('LOGLEVEL').upper())
    if isinstance(level, int):
        LOGLEVEL = level

logging.basicConfig(format='%(asctime)s %(levelname)s - %(name)s: %(message)s',
                    datefmt='%d.%m.%Y %H:%M',
                    level=LOGLEVEL)
logger = logging.getLogger(__name__)

logger.warning('Starting karen')

API_VERSION = os.getenv('KAREN_API_VERSION', '5.95')
logger.warning('Using API_VERSION %s', API_VERSION)

ACCESS_TOKEN = os.getenv('KAREN_ACCESS_TOKEN')
if not ACCESS_TOKEN:
    raise AssertionError('ACCESS_TOKEN required')

GROUP_ID = os.getenv('KAREN_GROUP_ID')
if GROUP_ID:
    logger.warning('Running as group #%s', GROUP_ID)

ADMIN_ID = os.getenv('KAREN_ADMIN_ID')
if ADMIN_ID:
    logger.warning('Using ADMIN_ID #%s', ADMIN_ID)
