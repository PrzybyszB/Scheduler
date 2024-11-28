FROM node:20.16.0

WORKDIR /frontend

COPY package.json yarn.lock ./

RUN yarn install --network-timeout 600000


COPY . .

RUN yarn run build

ENV NODE_ENV=production

CMD ["yarn", "start"]