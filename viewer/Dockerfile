FROM node:12

WORKDIR /app

COPY package.json /app

RUN chown -R node:node /app

USER node

RUN npm install

COPY static/ /app

COPY server.js /app

COPY index.html /app

EXPOSE 3001

CMD ["node","server"]

#https://bobcares.com/blog/node-js-application-with-docker-on-ubuntu/
# RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app
#https://levelup.gitconnected.com/set-up-and-run-a-simple-node-server-project-38b403a3dc09


