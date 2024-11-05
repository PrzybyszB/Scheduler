FROM node:20.16.0

WORKDIR /frontend

COPY package.json yarn.lock ./

RUN yarn install

COPY . .

RUN yarn run build

ENV NODE_ENV=production

CMD ["yarn", "start"]