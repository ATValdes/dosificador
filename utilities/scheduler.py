from crontab import CronTab

class Scheduler:
	def __init__(self, user="pi"):
		self.cron = CronTab(user=user)

	def clear(self):
		for job in self.cron:
			if job.comment == "water_analysis":
				self.cron.remove(job)
		self.cron.write()

	def schedule_next_job(self, url, minutes=0, hours=0):
		# job = self.cron.new(command=f"python {url}")
		# job.set_comment("water_analysis")
		# if minutes > 0:
		# 	job.minute.every(minutes)
		# 	self.cron.write()
		# else:
		# 	job.hour.every(hours)
		# 	self.cron.write()
		print(f"schedule next job, minutes: {minutes} hours: {hours}")
