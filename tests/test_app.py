from urllib.parse import quote


def activity_path(activity_name):
    return quote(activity_name, safe="")


def participant_path(email):
    return quote(email, safe="")


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["description"]
    assert activities["Chess Club"]["schedule"]
    assert activities["Chess Club"]["max_participants"] == 12
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant(client):
    email = "student@mergington.edu"

    response = client.post(
        f"/activities/{activity_path('Chess Club')}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Chess Club"
    }
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        f"/activities/{activity_path('Unknown Club')}/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_participant(client):
    email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{activity_path('Chess Club')}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_requires_email(client):
    response = client.post(
        f"/activities/{activity_path('Chess Club')}/signup"
    )

    assert response.status_code == 422


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_path('Chess Club')}/participants/{participant_path(email)}"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        f"/activities/{activity_path('Unknown Club')}/participants/"
        f"{participant_path('student@mergington.edu')}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    email = "student@mergington.edu"

    response = client.delete(
        f"/activities/{activity_path('Chess Club')}/participants/{participant_path(email)}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
