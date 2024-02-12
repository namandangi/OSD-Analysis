FROM postgis/postgis 
RUN apt-get update -y
RUN apt-get install  git postgresql-server-dev-15 make gcc -y
RUN apt  install postgresql-server-dev-all -y 
RUN apt install postgresql-16-pgvector -y
WORKDIR /tmp
RUN git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git && cd pgvector && make && make install