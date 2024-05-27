FROM python:3.12-slim

ENV APP_HOME /APP_HOME
WORKDIR ${APP_HOME}

COPY src/. src/.
COPY requirements.txt global_requirements.txt

# RUN pip install functions-framework
RUN pip install -r global_requirements.txt

# CMD exec functions-framework --target "get_health" --signature-type "http" --port 8080
CMD ["python", "src/app.py"]