
from faker import Faker
import random

fake = Faker("en_PH")


def generate_fake_user():
    gender = random.choice(["Male", "Female"])

    return {
        "full_name": fake.name_male() if gender == "Male" else fake.name_female(),
        "address": fake.street_address(),
        "birthdate": fake.date_of_birth(
            minimum_age=18,
            maximum_age=65
        ).isoformat(),
        "mobile_number": "09" + str(random.randint(100000000, 999999999)),
        "email": fake.email(),
        "gender": gender,
        "username": fake.user_name(),
        "city": fake.city(),
        "occupation": fake.job(),
        "postal_code": fake.postcode()
    }


def generate_multiple_users(quantity=10):
    return [generate_fake_user() for _ in range(quantity)]
