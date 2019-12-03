from faker import Faker
from faker.providers import BaseProvider
import random
import datetime
from dateutil.relativedelta import relativedelta


class Provider(BaseProvider):
    def username(self):
        return "{}{}{}{}".format(
            self.generator.first_name(),
            self.generator.random_element([".", "-", ""]),
            self.generator.last_name(),
            self.generator.random_int(),
        ).lower()

    def birth_date(self, max_age=80, min_age=18):
        return self.generator.date_between(
            start_date="-{}y".format(max_age), end_date="-{}y".format(min_age)
        )
