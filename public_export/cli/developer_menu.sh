#!/bin/bash
clear
echo -e "\e[36m=========================================\e[0m"
echo -e "\e[33m   KALI LINUX OSINT & PENTEST COMMANDER  \e[0m"
echo -e "\e[36m=========================================\e[0m"

# Dependency checks
has_docker=$(command -v docker >/dev/null 2>&1 && echo 1 || echo 0)
has_opencode=$(command -v opencode-pentest >/dev/null 2>&1 && echo 1 || echo 0)

if [ "$has_opencode" -eq 1 ]; then
    echo -e "   \e[32m[1] OpenCode Pentest Cycle (Interactive)\e[0m"
else
    echo -e "   \e[90m[1] OpenCode Pentest Cycle (Missing Executable)\e[0m"
fi

if [ "$has_docker" -eq 1 ]; then
    echo -e "   \e[32m[2] Docker Stack Command Hub\e[0m"
else
    echo -e "   \e[90m[2] Docker Stack Command Hub (Missing Docker)\e[0m"
fi

echo -e "   \e[32m[3] Remote VPS / VM SSH Connection Hub\e[0m"
echo -e "   \e[32m[4] Workspace Sync (GitHub & User Folder)\e[0m"

echo -e "\n\e[35m  GOVERNANCE & RULES:\e[0m"
echo -e "   \e[35m[L] Read & Enforce Universal AI Laws + Tools\e[0m"

echo -e "\n\e[37m   [Q] Exit to Base Bash Shell\e[0m"
echo -e "\e[36m=========================================\e[0m"

read -p "Select an option [1-4, L, Q]: " choice

case $choice in
    1)
        if [ "$has_opencode" -eq 1 ]; then
            read -p "Enter target/prompt for OpenCode Pentest Cycle: " target
            # Executes the actual pentest cycle tool dynamically linked in Kali
            opencode-pentest "$target"
        else
            echo -e "\e[31mopencode-pentest not found in Kali PATH.\e[0m"
        fi
        ;;
    2)
        if [ "$has_docker" -eq 1 ]; then
            echo -e "\e[36m--- Active Docker Containers ---\e[0m"
            sudo docker ps -a
            echo -e "\n\e[33mTip: Use 'sudo docker start <name>' to boot stopped tools.\e[0m"
        else
            echo -e "\e[31mDocker not installed on this WSL instance.\e[0m"
        fi
        ;;
    3)
        echo -e "\e[36m--- SSH Hub ---\e[0m"
        echo "Placeholder for VPS/VM connections."
        # Configure SSH targets here later
        ;;
    4)
        echo -e "\e[36m--- Syncing OSINT / Repos ---\e[0m"
        cd /mnt/c/OsintNeoAi && git status
        echo "Check complete."
        ;;
    [Ll]* )
        echo -e "\n\e[36m--- UNIVERSAL AI LAWS ---\e[0m"
        cat /mnt/c/Users/Amd949609/Desktop/00_ailaws.md
        echo -e "\n\e[36m--- AGENTS RULES ---\e[0m"
        if [ -f "/mnt/c/OsintNeoAi/AGENTS.md" ]; then
            cat /mnt/c/OsintNeoAi/AGENTS.md
        fi
        echo -e "\n\e[33mPress enter to return...\e[0m"
        read -r
        bash /mnt/c/OsintNeoAi/cli/developer_menu.sh
        ;;
    [Qq]* )
        exit 0
        ;;
    * )
        echo -e "\e[31mInvalid selection.\e[0m"
        ;;
esac
