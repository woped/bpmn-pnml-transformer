FROM python:3.12-slim

ENV APP_HOME /APP_HOME
WORKDIR ${APP_HOME}

# Copiying complete source code
COPY src/. src/.
# Copying the global requirements.txt
COPY requirements.txt global_requirements.txt

# move transformer python module within container to allow import from new entry point
RUN mv src/transform/transformer src/transformer

# installing all globally required dependencies
RUN pip install -r global_requirements.txt

CMD ["python", "src/app.py"]