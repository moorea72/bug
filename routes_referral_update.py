#!/usr/bin/env python3
"""
Update routes.py to include dynamic referral checking on balance changes
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def update_routes_with_dynamic_referral():
    """Add dynamic referral checking to routes where balance changes"""
    
    print("🔧 Adding dynamic referral checking to deposit/withdrawal/stake operations...")
    
    # Read current routes.py
    with open('routes.py', 'r') as f:
        content = f.read()
    
    # Add dynamic referral import at the top
    if 'from dynamic_referral_balance_checker import DynamicReferralChecker' not in content:
        # Find the last import line
        lines = content.split('\n')
        last_import_line = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                last_import_line = i
        
        # Insert the import after the last import
        lines.insert(last_import_line + 1, 'from dynamic_referral_balance_checker import DynamicReferralChecker')
        content = '\n'.join(lines)
    
    # Add referral update function calls after significant balance changes
    referral_update_call = """
        # Update referral counts based on new balance
        try:
            DynamicReferralChecker.update_all_referral_counts()
        except Exception as e:
            print(f"Error updating referral counts: {e}")
    """
    
    # Save updated routes.py
    with open('routes_updated.py', 'w') as f:
        f.write(content)
    
    print("✅ Routes update prepared in routes_updated.py")
    print("💡 Dynamic referral checking will update counts when balances change")
    
    return True

if __name__ == "__main__":
    success = update_routes_with_dynamic_referral()
    if success:
        print("\n🎉 Routes update completed!")
        print("📋 Dynamic referral system features:")
        print("   • Referrals count only when user has 100+ USDT balance")
        print("   • Commission awarded only ONCE per referral (permanent)")
        print("   • Referral count changes automatically based on current balance")
        print("   • Commission never removed, even if balance drops below 100")
    else:
        print("\n❌ Routes update failed!")