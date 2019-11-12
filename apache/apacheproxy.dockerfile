from httpd:2.4-alpine
## fix the base at 2.4 just in case

##pull the local httpd conf file in as the default configs
COPY httpd.conf /usr/local/apache2/conf/httpd.conf

# make folder for custom site configs to live in
RUN mkdir -p /usr/local/apache2/conf/sites/
