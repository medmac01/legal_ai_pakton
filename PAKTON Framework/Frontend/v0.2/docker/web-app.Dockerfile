# Dockerfile for web-app
FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./
COPY turbo.json ./

# Copy the entire project
COPY . .

# Install dependencies
RUN yarn install --frozen-lockfile

# Build the web app with the --no-lint flag to skip linting (we're in development mode)
RUN yarn workspace @opencanvas/web build --no-lint

# Set working directory to web app
WORKDIR /app/apps/web

# Expose the web app port
EXPOSE 3000

# Start the web app
CMD ["yarn", "start"]