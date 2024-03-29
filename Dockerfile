FROM python:3.10-slim

WORKDIR /app

RUN pip install pipenv

COPY hn_bot.py Pipfile Pipfile.lock /app/

RUN pipenv install --deploy --ignore-pipfile

CMD ["pipenv", "run", "python", "hn_bot.py"]
