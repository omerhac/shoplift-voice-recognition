FROM python:3.7

# Copy over and install the requirements
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# copy credentials  #TODO: change this!!!
COPY /credentials /credentials

EXPOSE 8080

WORKDIR /app

CMD python app.py