from password_validation import PasswordPolicy

pw_policy = PasswordPolicy(
    lowercase=1,
    uppercase=1,
    min_length=12,
    forbidden_words=['password']
)