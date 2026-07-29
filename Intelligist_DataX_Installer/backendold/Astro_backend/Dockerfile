FROM tiangolo/uwsgi-nginx:python3.7

RUN pip install -U pip
#RUN pip install --proxy=http://920181:zxcvbnm@proxy.customs.net:3128 -U pip

ENV NGINX_MAX_UPLOAD 0
ENV LISTEN_PORT 7000
ENV UWSGI_INI /app/uwsgi.ini
ENV STATIC_INDEX 0
ENV NGINX_WORKER_PROCESSES auto

# Install dependencies first (to enable caching)
COPY ./app/requirements.txt /app/requirements.txt
WORKDIR /app
RUN apt-get update && apt-get install -y python-dev libsasl2-modules libsasl2-dev gcc
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the rest of the application
ADD ./app /app

ENV PYTHONPATH=/app

ADD start.sh /start.sh
RUN chmod +x /start.sh
ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]

