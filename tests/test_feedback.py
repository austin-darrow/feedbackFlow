from fastapi.testclient import TestClient
from backend.main import app as fastapi_app
import os
import random
from services import db

client = TestClient(fastapi_app)

TEST_EMAIL = os.environ.get("TEST_EMAIL")
TEST_PASSWORD = os.environ.get("TEST_PASSWORD")

test_essay = '''
The Hobbit is an adventurous novel about a hobbit named Bilbo Baggins, who is asked by the wizard Gandalf to go on a dangerous journey. He joins a group of dwarves led by Thorin Oakenshield to reclaim their treasure from a dragon named Smaug. Along the way, they encounter many challenges like trolls, elves, and a creature called Gollum. Bilbo finds a magical ring in Gollum's cave that helps him escape, but he doesn't know how powerful it is at first. This ring later becomes the main focus of another book called The Lord of the Rings.

One of the main themes of The Hobbit is courage. Bilbo starts out as a timid hobbit who never leaves his home, but as the story progresses, he becomes braver and more confident. By the end of the journey, he is able to stand up to Smaug, showing that even the smallest person can make a big difference. This message is important because it teaches readers that anyone can be a hero, no matter how unlikely it seems.
'''

def random_email():
    return f"test{random.randint(0, 100000)}@example.com"

def setup_test_user_and_assignment():
    # Register a test user (if necessary)
    email = random_email()
    registration_response = client.post("/api/users", json={"email": email, "password": TEST_PASSWORD})
    assert registration_response.status_code == 200

    # Log in to get the access token
    response = client.post("/api/token", data={"username": email, "password": TEST_PASSWORD})
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    db_connection = db.get_connection()
    user = db.get_user(email, db_connection)

    response = client.post("/api/assignments", params={"title": "Test Assignment", "teacher_id": int(user["id"])})
    print(response.json())
    assert response.status_code == 200

    assignment_id = response.json()["assignment_id"]

    results = {
        "access_token": access_token,
        "email": email,
        "password": TEST_PASSWORD,
        "user_id": user["id"],
        "assignment_id": assignment_id
    }
    return results


def test_generate_feedback():
    setup = setup_test_user_and_assignment()

    headers = {"Authorization": f"Bearer {setup['access_token']}"}
    # Send the writing_sample in the JSON body, not as params
    json_payload = {"writing_sample": test_essay}

    response = client.post(
        f"/api/feedback/{setup['user_id']}/{setup['assignment_id']}",
        json=json_payload,  # Use json here instead of params
        headers=headers
    )

    assert response.status_code == 200
    response_text = response.json()['feedback']
    assert 'Glow' in response_text
    assert 'Grow' in response_text