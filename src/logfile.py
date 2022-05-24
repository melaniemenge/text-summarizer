import time

from colored_logs import logger

log = logger.Logger(id='Test-id-1')

log.start_process('This is taking a while')
time.sleep(3.5)
log.info('This is an info log while also logging the active process')

time.sleep(3.5)

duration_float_seconds = log.stop_process(
    log_type=logger.LogType.Success,
    values='Successfully finished task'
)