# ./react_frontend/Dockerfile
FROM node:14

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . ./

# Set the NODE_ENV to development by default if not specified
ENV NODE_ENV=development

CMD ["npm", "start"]