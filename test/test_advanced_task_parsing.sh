#!/bin/bash
# Test script for advanced task parsing with natural language

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_BASE="http://localhost:8000/api"

# Get JWT token (you need to replace this with your actual token)
# For testing, you can use the login endpoint or hardcode a token
echo -e "${YELLOW}=== Advanced Natural Language Task Parsing Tests ===${NC}\n"

# Test 1: Task with due date and priority
echo -e "${YELLOW}Test 1: Creating task with due date and priority${NC}"
echo "Message: 'I need to finish my FastAPI project by January 31st, it's really urgent'"
curl -N -X POST "${API_BASE}/chatkit/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "I need to finish my FastAPI project by January 31st, it is really urgent"
  }' 2>/dev/null
echo -e "\n"

# Test 2: Weekly recurring task
echo -e "${YELLOW}Test 2: Creating weekly recurring task${NC}"
echo "Message: 'Remind me to call mom every Sunday'"
curl -N -X POST "${API_BASE}/chatkit/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "Remind me to call mom every Sunday"
  }' 2>/dev/null
echo -e "\n"

# Test 3: Task with reminder
echo -e "${YELLOW}Test 3: Creating task with reminder${NC}"
echo "Message: 'Team meeting tomorrow at 10am, remind me 30 minutes before'"
curl -N -X POST "${API_BASE}/chatkit/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "Team meeting tomorrow at 10am, remind me 30 minutes before"
  }' 2>/dev/null
echo -e "\n"

# Test 4: Low priority task
echo -e "${YELLOW}Test 4: Creating low priority task${NC}"
echo "Message: 'Buy groceries when I have time, not urgent'"
curl -N -X POST "${API_BASE}/chatkit/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "Buy groceries when I have time, not urgent"
  }' 2>/dev/null
echo -e "\n"

# Test 5: Update existing task
echo -e "${YELLOW}Test 5: Updating task deadline${NC}"
echo "Message: 'Change task 18 deadline to February 15th'"
curl -N -X POST "${API_BASE}/chatkit/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "message": "Change task 18 deadline to February 15th"
  }' 2>/dev/null
echo -e "\n"

echo -e "${GREEN}=== Tests Complete ===${NC}"
echo -e "${YELLOW}Note: Replace YOUR_TOKEN_HERE with an actual JWT token from login${NC}"
