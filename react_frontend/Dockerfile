# Stage 1: Build the React app
FROM node:14 AS build

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: Serve the React app with NGINX
FROM nginx:alpine

# Copy the build files from the previous stage to the NGINX HTML directory
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80 for web traffic
EXPOSE 80

# Run NGINX in the foreground
CMD ["nginx", "-g", "daemon off;"]