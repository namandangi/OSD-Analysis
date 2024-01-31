
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir -r /code/requirements.txt

RUN pip install colormath pgvector
## TO DO, figure out the version and just put it in the requirements

COPY ./app /code/app

EXPOSE 85

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "85","--reload"]
