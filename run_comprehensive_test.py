"""
Simple test runner to verify system functionality
"""
if __name__ == "__main__":
    from comprehensive_verification_test import *
    
    print("Starting comprehensive system verification...")
    
    # Step 1: Reset database
    print("\n1. Resetting database...")
    reset_database_for_verification()
    
    # Step 2: Create test users
    print("\n2. Creating test users...")
    create_comprehensive_test_users()
    
    # Step 3: Create test data
    print("\n3. Creating test data...")
    users = User.query.filter_by(is_admin=False).all()
    create_comprehensive_test_data(users)
    
    # Step 4: Create default coins
    print("\n4. Creating default coins...")
    create_default_coins()
    
    # Step 5: Verify systems
    print("\n5. Verifying all systems...")
    verify_all_systems()
    
    print("\n✅ Comprehensive system verification completed!")