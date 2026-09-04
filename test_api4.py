from app import app
import json

with app.test_client() as c:
    # Need to mock the admin check or just bypass it.
    pass
