# This class uses static variables to store API keys 

class API_keys():
    
    @staticmethod
    def set_alpha_vantage_api_key(alpha_vantage_api_key):
        API_keys.alpha_vantage_api_key = alpha_vantage_api_key

    @staticmethod
    def get_alpha_vantage_api_key():
        return API_keys.alpha_vantage_api_key

    @staticmethod
    def set_finnhub_api_key(finnhub_api_key):
        API_keys.finnhub_api_key = finnhub_api_key

    @staticmethod
    def get_finnhub_api_key():
        return API_keys.finnhub_api_key
