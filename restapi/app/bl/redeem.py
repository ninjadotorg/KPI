from app import db
from app.models import User, Redeem
from app.tasks import send_renew_redeem_code
from app.helpers.utils import is_valid_email

import app.bl.referral as referral_bl


def issue_new_redeem_code_for_user(user_id, is_need_send_mail=True):
	u = User.find_user_with_id(user_id)
	if u is not None and is_valid_email(u.email):
		redeem = db.session.query(Redeem).filter(Redeem.reserved_id==0, Redeem.used_user==0).limit(1).first()
		referral_code = referral_bl.issue_referral_code_for_user(u)
		if redeem is not None:
			redeem.reserved_id = user_id
			db.session.flush()

			if is_need_send_mail:
				send_renew_redeem_code.delay(u.email, redeem.code, '{}prediction?refer={}'.format(g.BASE_URL, referral_code))
		