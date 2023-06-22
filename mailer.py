class Mailer:
    def __init__(self, config):
        self.receiver_email = config["receiver_email"]
        self.sender_email = config["sender_email"]
        self.password = config["password"]
        self.server = config["server"]
        self.port = config["port"]

    def send_daily_report(self, account):

        pass

    def send_error_message(self, param):

        pass

