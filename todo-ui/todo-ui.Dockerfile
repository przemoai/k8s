FROM node:21-bullseye-slim AS build

WORKDIR /dist/src/app

COPY todo-ui/. .

RUN npm install
RUN npm run build --prod


FROM nginx:latest AS ngi

COPY --from=build /dist/src/app/dist/todo-ui/browser /usr/share/nginx/html
COPY todo-ui/nginx.conf  /etc/nginx/conf.d/default.conf

EXPOSE 80
