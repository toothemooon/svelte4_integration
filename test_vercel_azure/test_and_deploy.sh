#!/bin/bash
# Test and deploy script for Vercel-Azure persistence fix

echo "===== Vercel-Azure Comment Persistence Test and Deployment ====="

# Color formatting for messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Run local database persistence test
echo -e "${YELLOW}Step 1: Testing database persistence locally...${NC}"
python test_vercel_azure/test_db_persistence.py

# Check if the test succeeded
if [ $? -ne 0 ]; then
    echo -e "${RED}Local persistence test failed. Please check the errors above.${NC}"
    exit 1
fi

echo -e "${GREEN}Local persistence test passed!${NC}"
echo ""

# Step 2: Ask if the user wants to deploy
echo -e "${YELLOW}Step 2: Deploy to Azure?${NC}"
read -p "Do you want to deploy the persistent version to Azure? (y/n): " deploy_choice

if [[ "$deploy_choice" == "y" || "$deploy_choice" == "Y" ]]; then
    echo -e "${YELLOW}Starting deployment to Azure...${NC}"
    bash test_vercel_azure/deploy-persistent.sh
    
    # Check if deployment succeeded
    if [ $? -ne 0 ]; then
        echo -e "${RED}Deployment failed. Please check the errors above.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Go to your Vercel-hosted frontend: https://your-vercel-app.vercel.app"
    echo "2. Add a comment to a blog post"
    echo "3. Refresh the page - your comment should still be there!"
    echo "4. Check Azure logs if needed: az webapp log tail --resource-group blog_quickstart --name sarada"
else
    echo "Deployment skipped. You can deploy later with: bash test_vercel_azure/deploy-persistent.sh"
fi

echo -e "${GREEN}Done!${NC}" 