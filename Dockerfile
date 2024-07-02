FROM python:3.9
WORKDIR /telemetry-processor
COPY . /telemetry-processor
#RUN pip install --upgrade pip
RUN pip3 install -r /telemetry-processor/requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["python3","telemetry-processor.py"]
