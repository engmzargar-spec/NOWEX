from apps.auth.models.user import User
from apps.scoring.models.user_score import UserScore  
from apps.kyc.models.kyc_models import KYCProfile
from apps.referral.models.referral_models import ReferralCode

def check_current_user():
    user_id = 'bf76777a-62a4-4008-9734-5ff57868e9cd'
    
    # بررسی وجود کاربر
    user = User.get_by_id(user_id)
    print('کاربر:', user.username if user else 'یافت نشد')
    
    # بررسی امتیاز
    score = UserScore.get_by_user_id(user_id)
    print('امتیاز:', score.total_score if score else 'یافت نشد')
    print('سطح Scoring:', score.score_level if score else 'یافت نشد')
    
    # بررسی KYC
    kyc = KYCProfile.get_by_user_id(user_id)
    print('سطح KYC:', kyc.kyc_level if kyc else 'یافت نشد')
    
    # بررسی کد معرف
    ref = ReferralCode.get_by_user_id(user_id)
    print('کد معرف:', ref.referral_code if ref else 'یافت نشد')

if __name__ == "__main__":
    check_current_user()