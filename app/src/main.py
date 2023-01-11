import logging
import time
import hookup
import settings


logging.basicConfig(format="%(levelname)s: %(name)s: %(asctime)s: %(message)s", level=settings.LOG_LEVEL)
logger = logging.getLogger("ad_resolver")

while True:
    logger.info("start iteration")
    try:
        hookup.run()
    except:
        logger.exception('Unhandled exception')
    # implicit timing
    logger.info("finish iteration") 
    time.sleep(settings.BATCH_INTERVAL)
