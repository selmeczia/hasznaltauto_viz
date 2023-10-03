FROM python:3.9

RUN pip install poetry
WORKDIR /app

COPY poetry.lock pyproject.toml /app/
COPY hasznaltauto_scraper /app/hasznaltauto_scraper

RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "-m", "hasznaltauto_scraper.app"]
