FROM python:3
RUN pip install bottle
COPY ./backend.py /app/backend.py
CMD ["python", "/app/backend.py"]