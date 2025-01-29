FROM python:3.12

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["fastapi", "run", "api/main.py", "--port", "8000"]