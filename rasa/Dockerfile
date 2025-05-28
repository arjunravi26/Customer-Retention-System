# FROM rasa/rasa:3.6.21-full

# # Switch to root user for apt-get and pip install
# USER root

# # Install build dependencies for tokenizers
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# # Update pip to the latest version
# RUN pip install --upgrade pip

# # Install Python dependencies
# WORKDIR /
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Switch to non-root user for running the application
# USER 1001

# # Copy Rasa project files
# COPY . .

# # Expose Rasa server port
# EXPOSE 5005

# # Run Rasa server with API enabled
# CMD ["rasa", "run", "--enable-api", "--cors", "*", "--port", "5005"]


# FROM rasa/rasa:3.6.21-full

# USER root

# RUN apt-get update && apt-get install -y \
#     build-essential supervisor \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*
# # RUN apt-get update \
# #     && apt-get install -y --no-install-recommends \
# #     build-essential supervisor g++ \
# #     && pip install --upgrade pip \
# #     && pip install --no-cache-dir -r requirements.txt \
# #     && apt-get purge -y --auto-remove \
# #     build-essential g++ \
# #     && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*


# RUN pip install --upgrade pip

# WORKDIR /

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .
# # RUN chown -R 1001:1001 /app

# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# EXPOSE 5005 5055
# ENTRYPOINT []
# CMD ["/usr/bin/supervisord"]

# FROM rasa/rasa:3.6.21-full

# USER root

# WORKDIR /

# COPY requirements.txt .

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#     build-essential supervisor g++ \
#     && pip install --upgrade pip \
#     && pip install --no-cache-dir -r requirements.txt \
#     && apt-get purge -y --auto-remove \
#     build-essential g++ \
#     && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# COPY . .

# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# EXPOSE 5005 5055

# ENTRYPOINT []
# CMD ["/usr/bin/supervisord"]



# # EXPOSE 5005

# # USER 1001
# # CMD ["rasa", "run", "--enable-api", "--cors", "*", "--port", "5005" && "rasa", "run", "--enable-api", "--cors", "*", "--port", "5006"]

FROM rasa/rasa:3.6.21-full

# Explicitly set root user for system-level operations
USER root

# Check for existing user/group and create if not present
RUN if ! getent group rasauser; then groupadd -g 1000 rasauser; fi && \
    if ! getent passwd rasauser; then useradd -m -u 1000 -g rasauser rasauser; fi && \
    mkdir -p /app /var/log/supervisor && \
    chown -R rasauser:rasauser /app /var/log/supervisor

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential supervisor g++ && \
    pip install --upgrade pip

# Set working directory and copy requirements
WORKDIR /
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove \
    build-essential g++ && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Copy project files
COPY . .

# Copy Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Switch to non-root user
USER rasauser

# Expose Rasa and action server ports
EXPOSE 5005 5055

# Run Supervisor with explicit config
ENTRYPOINT []
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]