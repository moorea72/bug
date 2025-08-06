
#!/usr/bin/env python3
"""
Database migration for 2 Friends Premium System
Removes referral commission columns and adds premium benefit columns
"""

from app import app, db
from models import User, ActivityLog
from sqlalchemy import text

def migrate_to_two_friends_system():
    """Migrate database from referral commission to 2 friends system"""
    
    with app.app_context():
        try:
            print("🔄 Migrating to 2 Friends Premium System...")
            
            # Add new columns if they don't exist
            try:
                db.session.execute(text('ALTER TABLE user ADD COLUMN two_friends_bonus_claimed BOOLEAN DEFAULT FALSE'))
                print("✅ Added two_friends_bonus_claimed column")
            except:
                print("ℹ️ two_friends_bonus_claimed column already exists")
            
            try:
                db.session.execute(text('ALTER TABLE user ADD COLUMN premium_benefits_active BOOLEAN DEFAULT FALSE'))
                print("✅ Added premium_benefits_active column")
            except:
                print("ℹ️ premium_benefits_active column already exists")
            
            try:
                db.session.execute(text('ALTER TABLE stake ADD COLUMN premium_commission FLOAT DEFAULT 0.0'))
                print("✅ Added premium_commission column to stakes")
            except:
                print("ℹ️ premium_commission column already exists")
            
            # Remove old referral commission columns if they exist
            try:
                db.session.execute(text('ALTER TABLE user DROP COLUMN referral_bonus'))
                print("✅ Removed referral_bonus column")
            except:
                print("ℹ️ referral_bonus column doesn't exist")
            
            try:
                db.session.execute(text('ALTER TABLE user DROP COLUMN current_referral_count'))
                print("✅ Removed current_referral_count column")
            except:
                print("ℹ️ current_referral_count column doesn't exist")
            
            # Clear old referral commission activity logs
            ActivityLog.query.filter(ActivityLog.action.like('%referral_commission%')).delete()
            print("✅ Cleared old referral commission logs")
            
            # Reset all users to default state
            db.session.execute(text('''
                UPDATE user SET 
                two_friends_bonus_claimed = FALSE,
                premium_benefits_active = FALSE
            '''))
            
            db.session.commit()
            
            print("\n🎉 Migration completed successfully!")
            print("📋 Changes made:")
            print("   • Removed referral commission system")
            print("   • Added 2 friends premium benefit system")
            print("   • Added premium commission tracking for stakes")
            print("   • Reset all users to default state")
            
            # Check qualified users
            users = User.query.all()
            qualified_users = 0
            
            for user in users:
                qualified_referrals = user.get_qualified_referrals_count()
                if qualified_referrals >= 2:
                    user.check_and_activate_premium_benefits()
                    qualified_users += 1
            
            db.session.commit()
            
            print(f"\n👥 User Status:")
            print(f"   • Total users: {len(users)}")
            print(f"   • Users with premium benefits: {qualified_users}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_to_two_friends_system()
