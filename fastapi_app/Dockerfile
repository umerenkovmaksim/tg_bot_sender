FROM python:3.12-slim

COPY . .
RUN pip install -r requirements.txt
RUN pip install uvicorn

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]