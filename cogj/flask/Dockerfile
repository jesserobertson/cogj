FROM developmentseed/geolambda:latest

# install app
#COPY . /build
#WORKDIR /build
#RUN \
#    pip install -r /build/requirements.txt; \
#    pip install . -v; \
#    rm -rf /build/*;

COPY lambda/lambda-package.sh /usr/local/bin/

COPY requirements.txt /home/geolambda/work/
RUN pip install -r /home/geolambda/work/requirements.txt

# @FIXME For dev only
RUN pip install uwsgi

COPY docker-entrypoint.sh /home/geolambda/work/

WORKDIR /home/geolambda/work/api/