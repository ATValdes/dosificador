import time

from error_handling.errors import DosifyNotWorking

def dosificar(errorHandler, resultado_analisis_viejo, camara, analizador, covertura_objetivo,
                tiempo=10, rango_error=0.1):

    # Activa el motor los primeros 10 segundos
    errorHandler.logger.info(f"Activando motor por {tiempo:.2f} segundos...")
    print(f"Activando motor por {tiempo:.2f} segundos...")
    activar_motor(tiempo)

    # Realiza un analisis del nuevo estado del bebedero
    resultado_analisis_nuevo = errorHandler.handle_image_errors(camara, analizador)
    resultado_final = abs(covertura_objetivo - resultado_analisis_nuevo)

    # El porcentaje de dosificacion cayo dentro del rango esperado
    if (resultado_final <= rango_error) or (resultado_analisis_nuevo >= covertura_objetivo):
        errorHandler.logger.info("Dosificacion realizada con exito")
        print("Dosificacion realizada con exito")
        return

    # Calcular cuánto aumentó la cobertura con la última activación
    porcentaje_llenado_en_dosificacion = resultado_analisis_nuevo - resultado_analisis_viejo

    #Error al detectar que no aumenta el porcentaje de covertura luego de activar el motor
    if porcentaje_llenado_en_dosificacion <= 0:
        raise DosifyNotWorking(tiempo)

    # Calcular la tasa de incremento por segundo
    tiempo_anterior = tiempo
    tasa_incremento = porcentaje_llenado_en_dosificacion / tiempo_anterior

    # Calcular el tiempo necesario para alcanzar el objetivo sin pasarse
    diferencia_restante = covertura_objetivo - resultado_analisis_nuevo
    nuevo_tiempo = diferencia_restante / tasa_incremento

    # Limitar el tiempo a valores positivos y realistas
    nuevo_tiempo = max(0, min(nuevo_tiempo, 20))  # Máximo 20 segundos de activación

    if nuevo_tiempo > 0:
        dosificar(errorHandler, resultado_analisis_nuevo, camara, analizador, covertura_objetivo,
                  nuevo_tiempo, rango_error)
    else:
        errorHandler.logger.info("No es necesario activar el motor, cobertura ya alcanzada.")
        print("No es necesario activar el motor, cobertura ya alcanzada.")


def activar_motor(delay):
    # activa motor
    print("Activando motor")
    time.sleep(delay)
    print("Desactivando motor")
    # desactiva motor
    print("Esperando 2 minutos a que las capsulas en el agua se estabilicen antes de proceder con el analisis")
    time.sleep(120)