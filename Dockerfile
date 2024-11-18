FROM python:3.11-slim-bookworm
COPY . /code/app
COPY ./requirements.txt /code/requirements.txt
WORKDIR /code/app
RUN pip install -r /code/requirements.txt
CMD ["uvicorn", "main:app", "--port", "8089", "--host", "0.0.0.0"]