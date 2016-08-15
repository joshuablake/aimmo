#!/usr/bin/env python
from worker_manager import WORKER_MANAGERS
import logging
import os

LOGGER = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)
    WorkerManagerClass = WORKER_MANAGERS[os.environ.get('WORKER_MANAGER', 'local')]
    worker_manager = WorkerManagerClass(os.environ.get('GAMES_API_URL',
                                        'http://localhost:8000/players/api/games/'))
    worker_manager.run()

if __name__ == '__main__':
    main()
