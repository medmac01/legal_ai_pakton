# Dockerfile for agent-server
FROM node:20-slim

# Install Python for any Python dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./
COPY turbo.json ./

# Copy the entire project
COPY . .

# Install dependencies
RUN yarn install --frozen-lockfile

# Build the project
RUN yarn workspace @opencanvas/agents build

# Set working directory to agents app
WORKDIR /app/apps/agents

# Expose the LangGraph server port
EXPOSE 54367

# Start the LangGraph server
CMD ["npx", "@langchain/langgraph-cli", "dev", "--port", "54367"]