# pwd_hash.py
import bcrypt
import sys
import getpass

def hash_password(password):
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against a bcrypt hash"""
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python pwd_hash.py hash <password>")
        print("  python pwd_hash.py verify <password> <hash>")
        print("  python pwd_hash.py interactive")
        return
    
    command = sys.argv[1]
    
    if command == "hash" and len(sys.argv) >= 3:
        password = sys.argv[2]
        hashed = hash_password(password)
        print(hashed)
        
    elif command == "verify" and len(sys.argv) >= 4:
        password = sys.argv[2]
        hashed = sys.argv[3]
        valid = verify_password(password, hashed)
        print(f"Valid: {valid}")
        
    elif command == "interactive":
        print("\nPassword Hash Utility")
        print("-" * 40)
        
        while True:
            print("\n1. Hash a password")
            print("2. Verify a password")
            print("3. Exit")
            
            choice = input("\nChoice: ").strip()
            
            if choice == "1":
                pwd = getpass.getpass("Enter password: ")
                hash_val = hash_password(pwd)
                print(f"\nHash: {hash_val}\n")
                print("-" * 40)
                
            elif choice == "2":
                pwd = getpass.getpass("Enter password: ")
                h = input("Enter hash: ")
                valid = verify_password(pwd, h)
                print(f"\nResult: {'✓ Valid' if valid else '✗ Invalid'}\n")
                print("-" * 40)
                
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice")
    else:
        print("Invalid command")

if __name__ == "__main__":
    main()