#!/bin/bash
# Script to extract translatable strings and update translation catalogs

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Extracting translatable strings...${NC}"

# Extract strings from source code to create template
pybabel extract \
    -F babel.cfg \
    -o src/dropjump/locales/kinemetry.pot \
    --project=Kinemetry \
    --version=0.1.0 \
    --copyright-holder="Kinemetry Contributors" \
    src/dropjump/

echo -e "${GREEN}✓ Created translation template: src/dropjump/locales/kinemetry.pot${NC}"

# Update Spanish catalog (create if doesn't exist)
if [ -f "src/dropjump/locales/es/LC_MESSAGES/kinemetry.po" ]; then
    echo -e "${BLUE}Updating Spanish translations...${NC}"
    pybabel update \
        -i src/dropjump/locales/kinemetry.pot \
        -d src/dropjump/locales \
        -l es
    echo -e "${GREEN}✓ Updated Spanish translations${NC}"
else
    echo -e "${BLUE}Creating Spanish translation catalog...${NC}"
    pybabel init \
        -i src/dropjump/locales/kinemetry.pot \
        -d src/dropjump/locales \
        -l es
    echo -e "${GREEN}✓ Created Spanish translation catalog${NC}"
fi

echo -e "${BLUE}Compiling translations...${NC}"
pybabel compile -d src/dropjump/locales

echo -e "${GREEN}✓ All translations compiled successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit src/dropjump/locales/es/LC_MESSAGES/kinemetry.po"
echo "2. Add Spanish translations for each msgstr"
echo "3. Run this script again to compile"
