import json
import os
from time import sleep
import shutil
import redis
from time import sleep

from light_emitting_desk.desk import Desk
from light_emitting_desk.utils import conf
from pathlib import Path


class Worker:
    """Worker to process the lighting jobs."""

    def __init__(self):
        """Construct."""
        self.redis = redis.Redis()

        desk_conf = conf["sectors"]
        if "TEST_SECTORS" in os.environ:  # nocov
            desk_conf = json.loads(os.environ["TEST_SECTORS"])

        self.desk = Desk(desk_conf)

    def process(self, job):
        """Process a job."""
        try:
            args = json.loads(job.decode("utf-8"))
            print(f"Got a job: {args}")

            if list(args.keys())[0] == "system":
                if "repeater" in args["system"]:
                    if args["system"]["repeater"] == "start":
                        print("Starting desk")
                        self.desk.light_up(
                            conf["defaults"]["colour"], {"mode": conf["defaults"]["mode"]}
                        )
                        shutil.copy(
                            "/home/pi/light-emitting-desk/etc/cron/repeater",
                            "/etc/cron.d/repeater",
                        )

                    if args["system"]["repeater"] == "stop":
                        print("Stopping desk")
                        Path("/etc/cron.d/repeater").unlink(missing_ok=True)
                        sleep(1)
                        self.redis.flushall()
                        sleep(1)
                        self.desk.light_up([0, 0, 0], {"mode": conf["defaults"]["mode"]})

            else:
                self.desk.light_up(args["colour"], args)

        except json.decoder.JSONDecodeError:  # nocov
            print("Your data is bad")

    def poll(self):
        """If there's a job on the queue, pull it off and process it."""
        data = self.redis.lpop("jobs")
        if data:
            self.process(data)

        else:  # nocov
            sleep(conf["worker"]["interval"])

    def work(self):  # nocov
        """Keep working forever."""
        while True:
            self.poll()


if __name__ == "__main__":  # nocov
    print("worker starting")
    worker = Worker()
    worker.work()
