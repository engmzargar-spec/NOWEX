import psycopg2

def check_scoring_record():
    try:
        # اتصال به دیتابیس Docker
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="nowex_db",
            user="postgres",  # کاربر پیش‌فرض Docker
            password="postgres"  # رمز پیش‌فرض Docker
        )
        
        cursor = conn.cursor()
        user_id = 'ab8a0554-e90f-4a58-bfb3-a9345670b696'
        
        # بررسی وجود رکورد scoring
        cursor.execute(
            "SELECT * FROM user_scores WHERE user_id = %s", 
            (user_id,)
        )
        score_record = cursor.fetchone()
        
        if score_record:
            print("✅ رکورد scoring وجود دارد:")
            print(f"امتیاز: {score_record[2]}")  # total_score
            print(f"سطح: {score_record[3]}")     # score_level
        else:
            print("❌ رکورد scoring وجود ندارد")
            
        # بررسی رکورد KYC
        cursor.execute(
            "SELECT kyc_level FROM kyc_profiles WHERE user_id = %s", 
            (user_id,)
        )
        kyc_record = cursor.fetchone()
        
        if kyc_record:
            print(f"✅ سطح KYC: {kyc_record[0]}")
        else:
            print("❌ رکورد KYC وجود ندارد")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"خطا: {e}")

if __name__ == "__main__":
    check_scoring_record()