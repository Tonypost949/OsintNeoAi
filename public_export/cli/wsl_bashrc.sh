if [ -f /etc/bash.bashrc ]; then
    . /etc/bash.bashrc
fi

export PATH=$PATH:/usr/local/bin:/home/osintneoai/.local/bin

# Export user Google Gemini API Key for OpenCode and Google AI tools
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
export GOOGLE_GENERATIVE_AI_API_KEY="YOUR_GOOGLE_GENERATIVE_AI_API_KEY_HERE"

function cli {
    developer-menu
}
alias launch=cli
