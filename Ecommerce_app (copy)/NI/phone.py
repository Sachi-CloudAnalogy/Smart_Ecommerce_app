# import random
from twilio.rest import Client

# otp = random.randint(1000, 9999)

account_sid = "ACaa062546f6a246251954bf4b6cf2bee2"
auth_token = "5ff2d511bc711411ee67db043d97980f"
verify_sid = "VA74862719853d791a2356ef7df0525f3c"
phone_no = "+918439715259"

client = Client(account_sid, auth_token)
# msg = client.messages.create(body=f"Your verification code is: {otp}",
#                              from_= "+13345085505",
#                              to=phone_no)

otp_verification = client.verify.services(verify_sid).verifications.create(to=phone_no, channel="sms")

otp_code = input("otp on phone")
otp_check = client.verify.services(verify_sid).verification_checks.create(to=phone_no, code=otp_code)

print(otp_check.status)

