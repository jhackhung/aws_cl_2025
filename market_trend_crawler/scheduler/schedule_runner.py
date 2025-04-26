import schedule
import time

class ScheduleRunner:
    def run(self):
        print("Starting scheduler...")

        def job():
            print("Running scheduled job...")

        schedule.every().day.at("10:00").do(job)

        while True:
            schedule.run_pending()
            time.sleep(1)