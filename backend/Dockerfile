FROM python:3.12.3

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --timeout 60 -r requirements.txt

RUN apt-get update

COPY ./AutoGrader .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]   