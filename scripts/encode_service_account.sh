#!/bin/bash

# Script to encode service_account.json for Render deployment
# This converts the JSON file to base64 format for environment variable

if [ ! -f "backend/service_account.json" ]; then
    echo "Error: backend/service_account.json not found"
    exit 1
fi

echo "Encoding service_account.json for Render..."
echo ""
echo "Copy the following (the entire base64 string) into Render as SERVICE_ACCOUNT_JSON environment variable:"
echo "========================================================"
cat backend/service_account.json | base64 -w 0
echo ""
echo "========================================================"
echo ""
echo "Done! Now paste this value in Render Dashboard:"
echo "1. Go to your Web Service settings"
echo "2. Navigate to Environment"
echo "3. Add new variable:"
echo "   - Name: SERVICE_ACCOUNT_JSON"
echo "   - Value: [paste the base64 string above]"
echo "4. Click Save"
