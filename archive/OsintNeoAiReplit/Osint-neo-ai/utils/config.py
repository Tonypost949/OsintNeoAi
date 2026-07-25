import os


class APIConfig:
    @staticmethod
    def get(key):
        return os.environ.get(key)

    @staticmethod
    def is_available(key):
        return bool(os.environ.get(key))

    @staticmethod
    def all_available():
        return {
            "OPENAI_API_KEY": APIConfig.is_available("OPENAI_API_KEY"),
            "IPINFO_API_KEY": APIConfig.is_available("IPINFO_API_KEY"),
            "SHODAN_API_KEY": APIConfig.is_available("SHODAN_API_KEY"),
            "ABUSEIPDB_API_KEY": APIConfig.is_available("ABUSEIPDB_API_KEY"),
            "VIRUSTOTAL_API_KEY": APIConfig.is_available("VIRUSTOTAL_API_KEY"),
            "NUMVERIFY_API_KEY": APIConfig.is_available("NUMVERIFY_API_KEY"),
            "TWILIO_ACCOUNT_SID": APIConfig.is_available("TWILIO_ACCOUNT_SID"),
            "TWILIO_AUTH_TOKEN": APIConfig.is_available("TWILIO_AUTH_TOKEN"),
            "GITHUB_TOKEN": APIConfig.is_available("GITHUB_TOKEN"),
            "REDDIT_CLIENT_ID": APIConfig.is_available("REDDIT_CLIENT_ID"),
            "REDDIT_CLIENT_SECRET": APIConfig.is_available("REDDIT_CLIENT_SECRET"),
            "TWITTER_BEARER_TOKEN": APIConfig.is_available("TWITTER_BEARER_TOKEN"),
            "GOOGLE_API_KEY": APIConfig.is_available("GOOGLE_API_KEY"),
        }
