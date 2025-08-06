
#!/usr/bin/env python3
"""
Reset all referral bonuses to zero and disable commission system
"""

from app import app, db
from models import User, ActivityLog

def reset_all_referral_bonuses():
    """Reset all referral bonuses to zero"""
    try:
        with app.app_context():
            print("🔄 Resetting all referral bonuses to zero...")
            
            # Reset all referral bonuses to 0
            users_updated = User.query.update({User.referral_bonus: 0.0})
            
            # Delete all referral commission logs
            commission_logs_deleted = ActivityLog.query.filter(
                ActivityLog.action.in_(['referral_commission', 'referral_bonus', 'referral_deposit_bonus'])
            ).delete()
            
            db.session.commit()
            
            print(f"✅ Reset complete:")
            print(f"   - {users_updated} users' referral bonuses reset to 0")
            print(f"   - {commission_logs_deleted} commission logs deleted")
            print(f"   - Referral commission system COMPLETELY DISABLED")
            
            return True
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error resetting referral bonuses: {e}")
        return False

if __name__ == "__main__":
    reset_all_referral_bonuses()
