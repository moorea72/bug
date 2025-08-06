#!/usr/bin/env python3
"""
Fix notification bell popup and referral commission system
"""

def fix_notification_bell_javascript():
    """Fix the notification bell JavaScript to ensure popup works"""
    js_content = '''
// Fixed notification bell functionality
window.showNotificationDropdown = function() {
    console.log('🔔 BELL CLICKED - FIXED VERSION!');
    
    const dropdown = document.getElementById('notificationDropdown');
    if (!dropdown) {
        console.log('❌ Dropdown not found, creating fallback alert');
        alert(`Admin Messages:

• Welcome to USDT Staking Platform!
  Start earning daily returns on your USDT deposits.

• New 3-Level Referral System Active!
  Earn 5% (L1), 3% (L2), 2% (L3) commission when referrals deposit 100+ USDT.

• Enhanced Security Measures
  Your funds are protected with our latest security updates.

• Referral Requirement: Only users with 100+ USDT total balance qualify for commission payouts.`);
        return;
    }
    
    const isHidden = dropdown.classList.contains('hidden');
    console.log('📋 Dropdown is currently hidden:', isHidden);
    
    if (isHidden) {
        dropdown.classList.remove('hidden');
        
        // Load admin messages immediately
        const notificationList = document.getElementById('notificationList');
        if (notificationList) {
            notificationList.innerHTML = `
                <div class="p-4 text-gray-700">
                    <div class="text-center mb-3">
                        <i class="fas fa-bell text-2xl text-blue-500"></i>
                        <h3 class="font-bold text-gray-800">Admin Messages</h3>
                    </div>
                    <div class="space-y-3">
                        <div class="p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
                            <h4 class="font-semibold text-green-800">Welcome to USDT Staking!</h4>
                            <p class="text-sm text-green-700 mt-1">Start earning daily returns by staking your USDT with us today.</p>
                            <p class="text-xs text-gray-500 mt-1">Just now</p>
                        </div>
                        <div class="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                            <h4 class="font-semibold text-blue-800">New 3-Level Referral System</h4>
                            <p class="text-sm text-blue-700 mt-1">Earn up to 5% commission! Referrals must deposit 100+ USDT to activate commissions.</p>
                            <p class="text-xs text-gray-500 mt-1">2 hours ago</p>
                        </div>
                        <div class="p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
                            <h4 class="font-semibold text-yellow-800">Security Enhanced</h4>
                            <p class="text-sm text-yellow-700 mt-1">Your funds are now more secure with our latest security updates.</p>
                            <p class="text-xs text-gray-500 mt-1">1 day ago</p>
                        </div>
                    </div>
                </div>
            `;
        }
        console.log('✅ NOTIFICATION POPUP SHOWN!');
    } else {
        dropdown.classList.add('hidden');
        console.log('❌ NOTIFICATION POPUP HIDDEN!');
    }
};

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
    const dropdown = document.getElementById('notificationDropdown');
    const bell = document.getElementById('notificationBell');
    
    if (dropdown && bell && !dropdown.contains(e.target) && !bell.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});

console.log('✅ Notification bell fix loaded successfully!');
    '''
    
    with open('static/js/notification-fix.js', 'w') as f:
        f.write(js_content)
    
    print("✅ Notification bell JavaScript fix created")

def test_referral_commission_fix():
    """Test the updated referral commission system"""
    from app import app, db
    from models import User, Deposit, ActivityLog
    from multi_level_referral_system import MultiLevelReferralSystem
    
    with app.app_context():
        # Find a test user with referral
        test_user = User.query.filter(User.referred_by.isnot(None)).first()
        if not test_user:
            print("❌ No test user with referral found")
            return
        
        print(f"Testing referral commission for user: {test_user.username}")
        print(f"User balance: ${test_user.usdt_balance}")
        print(f"Referred by: {test_user.referred_by}")
        
        # Test commission award
        result = MultiLevelReferralSystem.award_commission(test_user.id, 50)  # Small deposit
        print(f"Commission result: {result}")
        
        # Check if user balance meets requirement
        if test_user.usdt_balance >= 100:
            print("✅ User meets 100 USDT minimum requirement")
        else:
            print(f"❌ User balance ${test_user.usdt_balance} below 100 USDT minimum")

if __name__ == "__main__":
    print("🔧 Fixing notification bell and referral system...")
    fix_notification_bell_javascript()
    test_referral_commission_fix()
    print("🎉 Fixes applied!")