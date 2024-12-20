FROM python:3.12-slim

COPY . .

RUN pip install -r requirements.txt

WORKDIR /src/

EXPOSE 8000

CMD ["python", "bot.py"]