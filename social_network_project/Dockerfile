FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=social_network.settings
CMD ["gunicorn", "--bind", ":8000", "social_network.wsgi:application"]
