# You may need to specify the --platform depending on cloud provider
FROM python:3.9

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Next, copy in the .env file, which contains the PRODIGY_KEY variable
COPY .env .

# Install everything
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt && \
    export $(cat .env) && \
    python -m pip install prodigy -f https://${PRODIGY_KEY}@download.prodi.gy

# Copy the rest in, keeping .dockerignore in mind
COPY . .

RUN python -m pip install .

# Set some environment variables
ENV PRODIGY_LOGGING "basic"
ENV PRODIGY_ALLOWED_SESSIONS "emirkan,michel,vincent"
ENV PRODIGY_BASIC_AUTH_USER "prodigy-user"

# Expose the port number appropriate for cloud vendor
EXPOSE 8080

CMD [ "/app/scripts/start.sh" ]
