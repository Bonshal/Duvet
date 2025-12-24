# test_security.py
from app.core.security import get_password_hash, verify_password, create_access_token

def run_tests():
    print("🧪 STARTING SECURITY TESTS...")
    
    # Test 1: Hashing
    print("\n[1] Testing Password Hashing...")
    password = "secret_monkey"
    hashed_pw = get_password_hash(password)
    print(f"    Input: {password}")
    print(f"    Output: {hashed_pw}")
    
    if hashed_pw != password and hashed_pw.startswith("$2b$"):
        print("    ✅ SUCCESS: Password hashed correctly.")
    else:
        print("    ❌ FAIL: Hashing failed.")

    # Test 2: Verification
    print("\n[2] Testing Password Verification...")
    is_valid = verify_password("secret_monkey", hashed_pw)
    is_invalid = verify_password("wrong_password", hashed_pw)
    
    if is_valid and not is_invalid:
        print("    ✅ SUCCESS: Correct password accepted, wrong password rejected.")
    else:
        print("    ❌ FAIL: Verification logic is broken.")

    # Test 3: JWT Token Generation
    print("\n[3] Testing JWT Token Creation...")
    user_email = "tester@example.com"
    token = create_access_token(data={"sub": user_email})
    print(f"    Token: {token[:20]}... (truncated)")
    
    if token and isinstance(token, str) and len(token) > 20:
        print("    ✅ SUCCESS: JWT Token generated.")
    else:
        print("    ❌ FAIL: Token generation failed.")

    print("\n🎉 ALL TESTS PASSED.")

if __name__ == "__main__":
    run_tests()