FROM python:3.5

WORKDIR "/app"
RUN git clone https://github.com/pozyxLabs/Pozyx-Python-library.git
WORKDIR "/app/Pozyx-Python-library"
RUN python setup.py install
WORKDIR "/app"
COPY requirements.txt /app/
WORKDIR "/app"
RUN pip install -r requirements.txt
COPY . /app

CMD ["python", "main.py"]