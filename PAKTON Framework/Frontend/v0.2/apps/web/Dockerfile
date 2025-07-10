# Builder stage
FROM node:20-slim AS builder

WORKDIR /app

# Copy root package.json and workspace files
COPY package.json yarn.lock ./
COPY packages ./packages

# Copy the web app
COPY apps/web ./apps/web

# Install dependencies
RUN yarn install --frozen-lockfile

# Build the app
RUN yarn workspace @opencanvas/web build

# Production image
FROM node:20-slim

WORKDIR /app

# Copy necessary files from the builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/packages ./packages
COPY --from=builder /app/apps/web/.next ./apps/web/.next
COPY --from=builder /app/apps/web/package.json ./apps/web/package.json
COPY --from=builder /app/apps/web/next.config.js ./apps/web/next.config.js
COPY --from=builder /app/apps/web/public ./apps/web/public

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

WORKDIR /app/apps/web

# Expose port for the app
EXPOSE 3000

# Command to run the app
CMD ["yarn", "start"]