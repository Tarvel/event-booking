# stagone: builder
FROM python:3.11-slim AS builder

# Create and set working folder
WORKDIR /app

# environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .


# collect static files
RUN python manage.py collectstatic --noinput || echo "collectstatic failed (probably not needed yet)"

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]



# Stage two: production

FROM python:3.11-slim

# Create user and directories
RUN useradd -m -r appuser && mkdir /app && chown -R appuser /app
WORKDIR /app

# Copy Python deps and project code from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --chown=appuser:appuser . .

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /app/staticfiles && chown -R appuser:appuser /app/staticfiles

USER appuser

EXPOSE 8000

RUN chmod +x /app/build.sh

CMD ["/app/build.sh"]
