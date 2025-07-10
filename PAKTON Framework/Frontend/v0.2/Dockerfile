# Multi-stage build for Open Canvas
FROM node:20-slim AS builder

# Install required dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./
COPY packages/shared/package.json ./packages/shared/
COPY apps/web/package.json ./apps/web/
COPY apps/agents/package.json ./apps/agents/

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy the rest of the application
COPY . .

# Build the shared package and all applications
RUN yarn build

# Production stage for Next.js frontend
FROM node:20-slim AS frontend

WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /app/package.json /app/yarn.lock ./
COPY --from=builder /app/packages/shared/package.json ./packages/shared/
COPY --from=builder /app/apps/web/package.json ./apps/web/
COPY --from=builder /app/packages/shared/dist ./packages/shared/dist
COPY --from=builder /app/apps/web/.next ./apps/web/.next
COPY --from=builder /app/apps/web/public ./apps/web/public
COPY --from=builder /app/apps/web/next.config.js ./apps/web/

# Install production dependencies only
RUN yarn install --frozen-lockfile --production

# Set working directory to web app for running the server
WORKDIR /app/apps/web

# Expose port
EXPOSE 3000

# Command to run Next.js in production
CMD ["yarn", "start"]

# Production stage for LangGraph agents
FROM node:20-slim AS agents

# Install Python dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /app/package.json /app/yarn.lock ./
COPY --from=builder /app/packages/shared/package.json ./packages/shared/
COPY --from=builder /app/apps/agents/package.json ./apps/agents/
COPY --from=builder /app/packages/shared/dist ./packages/shared/dist
COPY --from=builder /app/apps/agents/dist ./apps/agents/dist
COPY --from=builder /app/apps/agents/src ./apps/agents/src

# Install LangGraph CLI
RUN pip3 install langchain-cli langchain-langgraph

# Install production dependencies only
RUN yarn install --frozen-lockfile --production

# Set working directory to agents app
WORKDIR /app/apps/agents

# Expose port for LangGraph server
EXPOSE 54367

# Command to run LangGraph server in production
CMD ["npx", "@langchain/langgraph-cli", "serve", "--port", "54367"]