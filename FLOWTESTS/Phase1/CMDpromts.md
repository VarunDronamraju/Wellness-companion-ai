# step123

cd wellness-companion-ai
cp .env.example .env
# Edit .env with your values
docker-compose up -d

#gitpush
#!/bin/bash

# TASK: Add project structure, commit, tag as phase0.03, and push to GitHub

# Navigate to the WellnessAtWorkAI directory (if not already there)
cd /c/Users/varun/Desktop/JObSearch/Application/WellnessAtWorkAI

# Add all files, including the wellness-companion-ai directory
git add wellness-companion-ai

# Commit changes with a message
git commit -m "Phase0.3: Add full project structure for wellness-companion-ai"

# Tag the commit with version 'phase0.03'
git tag -a phase0.03 -m "Version phase0.03: Full project structure and README"

# Push to remote repository (main branch should already be set up)
git push origin main

# Push the tag to the remote repository
git push origin phase0.03

echo "✅ Project structure added and pushed to GitHub"
echo "📌 Version tagged as 'phase0.03'"
echo "🌐 Repository: https://github.com/VarunDronamraju/Wellness-companion-ai.git"
echo "🚀 Main branch and tag pushed successfully"

-------------------------------------------------------------------------------------------------------------------------------------------------------

# tep456


In git bah
# Test all database services
chmod +x test_database_services.sh
./test_database_services.sh
