FROM nginx:1.15.7-alpine
MAINTAINER Keith Moss <keithamoss@gmail.com>

RUN cp /etc/nginx/uwsgi_params /var/tmp/uwsgi_params
# Copy our local nginx config in
RUN rm -rf /etc/nginx
COPY nginx /etc/nginx
RUN cp /var/tmp/uwsgi_params /etc/nginx/uwsgi_params

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]