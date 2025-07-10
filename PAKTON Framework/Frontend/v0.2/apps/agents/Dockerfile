FROM node:20-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./
COPY turbo.json ./   
COPY packages ./packages
COPY apps/agents/package.json ./apps/agents/

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy the agent server code
COPY apps/agents ./apps/agents

# Install langchain and other Python dependencies
RUN pip3 install langchain langchain-cli langchain-langgraph

# Set working directory to the agents app
WORKDIR /app/apps/agents

# Build the agent server
RUN yarn build

# Expose LangGraph server port
EXPOSE 54367

# Start LangGraph server
CMD ["npx", "@langchain/langgraph-cli", "serve", "--port", "54367"]