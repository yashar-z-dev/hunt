class BrowserConfig:
    def __init__(self):
        self.base_url = self.get_base_url()
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 5
        self.rate_limit = 1
        self.fields = self.get_fields()
        self.validation_rules = self.get_validation_rules()

    def get_base_url(self):
        return "https://api.yeswehack.com/programs?page=3&resultsPerPage=42&filter%5Btype%5D%5B%5D=bug-bounty"
        """
        a = 'https://api.yeswehack.com/programs/filters-data?filter%5Btype%5D%5B%5D=bug-bounty'
        b = 'https://api.yeswehack.com/programs?page=2&resultsPerPage=42&filter%5Btype%5D%5B%5D=bug-bounty'
        c = 'https://api.yeswehack.com/programs/count'
        d = "https://api.yeswehack.com/programs?page=1&resultsPerPage=100&filter%5Btype%5D%5B%5D=bug-bounty"
        """

    def get_fields(self):
        return {
            "title": {"path": ["title"], "default": "N/A"},
            "last_update_at": {"path": ["last_update_at"], "default": None}
            }
    
    def get_validation_rules(self):
        return [
            {"key": "items"},  # dataset must contain "items"
        ]