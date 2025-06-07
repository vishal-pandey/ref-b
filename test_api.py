\
import requests
import uuid
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

# Helper to print test results
def print_test_result(test_name, success, response_data=None, error_message=None):
    status = "PASSED" if success else "FAILED"
    print(f"Test: {test_name} - {status}")
    if response_data:
        print(f"  Response: {response_data}")
    if error_message:
        print(f"  Error: {error_message}")
    print("---")

# --- Auth Endpoints --- 
def test_request_otp_email():
    test_name = "Request OTP via Email"
    payload = {"email": "test@example.com"}
    try:
        response = requests.post(f"{BASE_URL}/auth/request-otp", json=payload)
        if response.status_code == 200 and response.json().get("msg") == "OTP sent successfully":
            print_test_result(test_name, True, response.json())
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

def test_request_otp_mobile():
    test_name = "Request OTP via Mobile"
    # Note: Update with a valid E.164 number if your validation is strict
    payload = {"mobile_number": "+12345678900"} 
    try:
        response = requests.post(f"{BASE_URL}/auth/request-otp", json=payload)
        if response.status_code == 200 and response.json().get("msg") == "OTP sent successfully":
            print_test_result(test_name, True, response.json())
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

# Note: Verification of OTP requires a real OTP from the backend. 
# This test will likely fail unless you manually provide a valid OTP.
def test_verify_otp_email(otp_code="123456"): # Placeholder OTP
    test_name = "Verify OTP (Email)"
    payload = {"email": "test@example.com", "otp_code": otp_code}
    try:
        response = requests.post(f"{BASE_URL}/auth/verify-otp", json=payload)
        if response.status_code == 200 and "access_token" in response.json():
            print_test_result(test_name, True, response.json().get("token_type"))
            return response.json().get("access_token") # Return token for subsequent tests
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return None

# --- Job Endpoints (Protected - assuming some require auth, though not implemented yet) ---
# For now, these tests don't use an auth token. This will need to be added once auth is enforced.

new_job_id = None

def test_create_job_posting():
    global new_job_id
    test_name = "Create Job Posting"
    payload = {
        "RoleName": "Test Role",
        "CompanyName": "Test Company",
        "JobDescription": "Test Description",
        "Location": "Test Location"
    }
    try:
        response = requests.post(f"{BASE_URL}/jobs/", json=payload)
        if response.status_code == 201:
            new_job_id = response.json().get("id")
            print_test_result(test_name, True, response.json().get("id"))
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

def test_read_job_postings():
    test_name = "Read Job Postings"
    try:
        response = requests.get(f"{BASE_URL}/jobs/")
        if response.status_code == 200 and isinstance(response.json(), list):
            print_test_result(test_name, True, f"Found {len(response.json())} jobs")
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

def test_read_specific_job_posting():
    test_name = "Read Specific Job Posting"
    if not new_job_id:
        print_test_result(test_name, False, error_message="No job ID from create test.")
        return False
    try:
        response = requests.get(f"{BASE_URL}/jobs/{new_job_id}")
        if response.status_code == 200 and response.json().get("id") == new_job_id:
            print_test_result(test_name, True, response.json().get("RoleName"))
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

def test_update_job_posting():
    test_name = "Update Job Posting"
    if not new_job_id:
        print_test_result(test_name, False, error_message="No job ID from create test.")
        return False
    payload = {"RoleName": "Updated Test Role", "JobDescription": "Updated Description"}
    try:
        response = requests.put(f"{BASE_URL}/jobs/{new_job_id}", json=payload)
        if response.status_code == 200 and response.json().get("RoleName") == "Updated Test Role":
            print_test_result(test_name, True, response.json().get("RoleName"))
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

def test_search_jobs():
    test_name = "Search Jobs (RoleName)"
    try:
        response = requests.get(f"{BASE_URL}/jobs/?RoleName=Updated Test Role")
        if response.status_code == 200 and isinstance(response.json(), list):
            found = any(job.get("RoleName") == "Updated Test Role" for job in response.json())
            print_test_result(test_name, True, f"Found: {found}, Count: {len(response.json())}")
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

# --- Job Suggestion Endpoints ---
def test_get_role_name_suggestions():
    test_name = "Get Role Name Suggestions"
    try:
        response = requests.get(f"{BASE_URL}/jobs/suggestions/role-names")
        if response.status_code == 200 and "suggestions" in response.json():
            print_test_result(test_name, True, f"Got {len(response.json()['suggestions'])} suggestions")
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

def test_get_company_name_suggestions():
    test_name = "Get Company Name Suggestions"
    try:
        response = requests.get(f"{BASE_URL}/jobs/suggestions/company-names")
        if response.status_code == 200 and "suggestions" in response.json():
            print_test_result(test_name, True, f"Got {len(response.json()['suggestions'])} suggestions")
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

def test_get_location_suggestions():
    test_name = "Get Location Suggestions"
    try:
        response = requests.get(f"{BASE_URL}/jobs/suggestions/locations")
        if response.status_code == 200 and "suggestions" in response.json():
            print_test_result(test_name, True, f"Got {len(response.json()['suggestions'])} suggestions")
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

def test_get_department_name_suggestions():
    test_name = "Get Department Name Suggestions"
    try:
        response = requests.get(f"{BASE_URL}/jobs/suggestions/department-names") # Assuming this path
        if response.status_code == 200 and "suggestions" in response.json():
            print_test_result(test_name, True, f"Got {len(response.json()['suggestions'])} suggestions")
            return True
        else:
            print_test_result(test_name, False, response.json(), f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

def test_delete_job_posting():
    test_name = "Delete Job Posting"
    if not new_job_id:
        print_test_result(test_name, False, error_message="No job ID from create test.")
        return False
    try:
        response = requests.delete(f"{BASE_URL}/jobs/{new_job_id}")
        if response.status_code == 204:
            print_test_result(test_name, True)
            # Verify deletion
            verify_response = requests.get(f"{BASE_URL}/jobs/{new_job_id}")
            if verify_response.status_code == 404:
                print_test_result(f"{test_name} - Verification", True, "Job confirmed deleted")
                return True
            else:
                print_test_result(f"{test_name} - Verification", False, "Job still exists after delete attempt")
                return False
        else:
            print_test_result(test_name, False, response.text, f"Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_test_result(test_name, False, error_message=str(e))
        return False

if __name__ == "__main__":
    print("Starting API tests...")
    
    # Auth tests
    test_request_otp_email()
    test_request_otp_mobile()
    # access_token = test_verify_otp_email() # This will likely fail without a real OTP
    # print(f"Retrieved Access Token: {access_token}") 
    # TODO: Pass access_token to protected endpoints once auth is enforced

    # Job CRUD and Search tests
    if test_create_job_posting():
        test_read_specific_job_posting()
        test_update_job_posting()
        test_search_jobs() # Search for the updated role
    test_read_job_postings() # General read
    
    # Suggestion tests
    test_get_role_name_suggestions()
    # Add calls for other suggestion endpoints here
    test_get_company_name_suggestions()
    test_get_location_suggestions()
    test_get_department_name_suggestions()

    # Cleanup
    if new_job_id: # Only attempt delete if a job was created
        test_delete_job_posting()

    print("API tests completed.")
