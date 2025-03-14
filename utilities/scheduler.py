from crontab import CronTab
from datetime import datetime, timedelta


class Scheduler:
	def __init__(self, user="pi"):
		self.cron = CronTab(user=user)

	def clear(self):
		for job in self.cron:
			if job.comment == "water_analysis":
				self.cron.remove(job)
		self.cron.write()

	def schedule_next_job(self, url, minutes=0, hours=0, time_of_script_init=datetime.now()):
		job = self.cron.new(command=f"python {url}")
		job.set_comment("water_analysis")

		if minutes == 0 and hours == 0:
			raise ValueError("Debes especificar al menos minutos o horas para la ejecución.")

        # Calcular el tiempo de ejecución
		future_time = time_of_script_init + timedelta(hours=hours, minutes=minutes)

		# Reprogramar si cae fuera del horario permitido (20:00 - 06:00)
		if future_time.hour >= 20 or future_time.hour < 6:
			future_time = future_time.replace(hour=6, minute=0) + timedelta(days=1)
			print("La ejecución cae en un horario nocturno. Se ha reprogramado a las 06:00 AM.")
	
		# Configurar la ejecución en la hora exacta
		job.minute.on(future_time.minute)
		job.hour.on(future_time.hour)

        # Guardar en crontab
		self.cron.write()
	
		print(f"Tarea programada para ejecutarse a las {future_time.strftime('%Y-%m-%d %H:%M')}")
	
	def list_scheduled_jobs(self):
		result = []
		for job in self.cron:
			if job.comment == "water_analysis":
				result.append(job.command)
		return result
