
docker stop osd-analysis-api
docker rm osd-analysis-api
# docker run -it -v ${PWD}/app:/code/app --name dsapostgisapi -p 82:82 dsapostgisapi /bin/bash
docker run -it --name osd-analysis-api -p 85:85 osd-analysis-api-image
