class BaseSmsReceiver:
    def get_phone_number(self):
        raise NotImplementedError(
            "Implement 'get_phone_number' in {name}".format(
                name=self.__class__.__name__
            )
        )

    def get_latest_sms(self, phone_number):
        raise NotImplementedError(
            "Implement 'get_latest_sms' in {name}".format(name=self.__class__.__name__)
        )


class ManualSmsReceiver(BaseSmsReceiver):
    def get_phone_number(self):
        return input("Provide phone number:")

    def get_latest_sms(self, phone_number):
        return input("Provide latest SMS content:")
