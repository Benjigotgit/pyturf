FROM tiangolo/uwsgi-nginx-flask:python3.8-alpine
RUN apk --update add bash nano
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static

COPY ./algorithms /var/www/algorithms
COPY ./perf-tests /var/www/perf-tests
COPY ./test-geojson /var/www/test-geojson
COPY ./requirements.txt /var/www/requirements.txt

RUN pip install -r /var/www/requirements.txt

