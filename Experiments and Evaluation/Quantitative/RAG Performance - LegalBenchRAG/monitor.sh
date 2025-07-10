#!/bin/bash

# this script monitors the health of a Docker container running the MultiAgentFramework service
# and attempts to restart it if it becomes unresponsive. 

# Configuration
SERVICE_CONTAINER="multiagentframework_service"
HEALTH_ENDPOINT="http://localhost:5001/health"
TIMEOUT=10  # Timeout in seconds for curl
CHECK_INTERVAL=60  # Check every 60 seconds
LOG_FILE="./docker-health-monitor.log"
# Set the path to your docker-compose.yml file directory
COMPOSE_DIR="path_to_api_/MultiAgentFramework/API"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yml"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Create log file if it doesn't exist
touch "$LOG_FILE"
log_message "Starting health monitoring for $SERVICE_CONTAINER"
log_message "Using docker-compose file: $COMPOSE_FILE"

# Main monitoring loop
while true; do
    log_message "Checking health endpoint: $HEALTH_ENDPOINT"
    
    # Check if the container is running
    if ! docker ps | grep -q "$SERVICE_CONTAINER"; then
        log_message "ERROR: Container $SERVICE_CONTAINER is not running. Attempting to start it..."
        # Try starting with docker-compose
        if [ -f "$COMPOSE_FILE" ]; then
            cd "$COMPOSE_DIR" && docker-compose up -d "$SERVICE_CONTAINER"
            RESULT=$?
            if [ $RESULT -eq 0 ]; then
                log_message "Container start command executed. Waiting for container to start..."
            else
                log_message "WARNING: Failed to start container with docker-compose. Exit code: $RESULT"
                # Fallback to direct docker start
                docker start "$SERVICE_CONTAINER"
                log_message "Attempted direct docker start as fallback"
            fi
        else
            log_message "WARNING: docker-compose file not found at $COMPOSE_FILE"
            # Fallback to direct docker start
            docker start "$SERVICE_CONTAINER"
            log_message "Attempted direct docker start as fallback"
        fi
        
        sleep 45  # Give it extra time to start up
        continue
    fi
    
    # Check if the health endpoint responds
    if curl -s --max-time "$TIMEOUT" "$HEALTH_ENDPOINT" > /dev/null; then
        log_message "Health check successful"
    else
        log_message "ERROR: Health check failed for $SERVICE_CONTAINER. Attempting restart..."
        
        # Try restarting with docker-compose
        if [ -f "$COMPOSE_FILE" ]; then
            log_message "Trying docker-compose restart..."
            cd "$COMPOSE_DIR" && docker-compose restart "$SERVICE_CONTAINER"
            COMPOSE_RESULT=$?
            
            if [ $COMPOSE_RESULT -eq 0 ]; then
                log_message "docker-compose restart command executed successfully"
            else
                log_message "WARNING: docker-compose restart failed with exit code: $COMPOSE_RESULT"
                # If docker-compose restart failed, try direct docker restart
                log_message "Falling back to direct docker restart..."
                docker restart "$SERVICE_CONTAINER"
                log_message "Direct docker restart attempted as fallback"
            fi
        else
            log_message "WARNING: docker-compose file not found at $COMPOSE_FILE"
            # Fallback to more aggressive direct docker restart
            log_message "Using direct docker stop/start method..."
            docker stop "$SERVICE_CONTAINER"
            sleep 5
            docker start "$SERVICE_CONTAINER"
            log_message "Direct docker stop/start sequence completed"
        fi
        
        # Wait for service to restart before next check
        log_message "Waiting for container to restart..."
        sleep 45  # Give it extra time to restart
        
        # Verify the restart worked
        if docker ps | grep -q "$SERVICE_CONTAINER"; then
            log_message "Container is now running after restart attempt"
            # Check health after restart
            if curl -s --max-time "$TIMEOUT" "$HEALTH_ENDPOINT" > /dev/null; then
                log_message "Health check successful after restart"
            else
                log_message "WARNING: Container is running but health check still failing after restart"
            fi
        else
            log_message "WARNING: Container is still not running after restart attempt"
        fi
    fi
    
    # Wait for the next check interval
    log_message "Sleeping for $CHECK_INTERVAL seconds until next check"
    sleep "$CHECK_INTERVAL"
done