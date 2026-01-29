from celery import shared_task
from app.services.accompaniment_service import generate_accompaniment


@shared_task(name="accompaniment.generate")
def accompaniment_generate(input_path: str):
    return generate_accompaniment(input_path)

