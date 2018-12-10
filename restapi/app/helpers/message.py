#!/usr/bin/python
# -*- coding: utf-8 -*-

class MESSAGE(object):
	# ERROR
	INVALID_DATA = 'Please double check your input data.'
	INVALID_BET = 'No equivalent bets found. Please create a new bet.'
	INVALID_ADDRESS = 'Please provide valid wallet address!'
	MISSING_OFFCHAIN = 'Missing offchain data!'
	INVALID_ODDS = 'Odds shoule be large than 1'
	MAXIMUM_FREE_BET = 'The maximum free bet is 100!'
	FREE_BET_UNABLE = 'The free bet is unable!'
	WATTING_TIME_FREE_BET = 'Please watting to next free bet'
	CANNOT_WITHDRAW = 'You cannot withdraw this handshake!'
	CANNOT_ROLLBACK = 'Cannot rollback this handshake!'
	CANNOT_VERIFY_EMAIL = 'Cannot verification email!'
	CANNOT_UNSUBSCRIBE_EMAIL = 'Cannot unsubscribe email!'
	FILE_TOO_LARGE = 'File too large!'
	EMAIL_ALREADY_SUBSCRIBED = 'Your email is already registered!'

	# OUTCOME
	OUTCOME_INVALID = 'Please check your outcome id'
	OUTCOME_INVALID_RESULT = 'Please check your outcome result'
	OUTCOME_HAS_RESULT = 'This outcome has had result already!'
	OUTCOME_IS_REPORTING = 'This outcome is reporting!'

	# MATCH
	MATCH_NOT_FOUND = 'Match not found. Please try again.'
	MATCH_INVALID_RESULT = 'Match result invalid. Please try again.'
	MATCH_RESULT_EMPTY = 'Match result is empty. Please try again.'
	MATCH_CANNOT_SET_RESULT = 'The report time is exceed!'
	MATCH_INVALID_TIME = 'Please double check your closing time, report time and dispute time'
	MATCH_HAS_BEEN_REVIEWED = 'This event has been reviewed already!'
	MATCH_SOURCE_EMPTY = 'Source is empty. Please try again.'

	# USER
	USER_INVALID_EMAIL = 'Please enter a valid email address.'
	USER_CANNOT_REGISTRY = 'Sorry, we were unable to register you. Please contact human@autonomous.ai for support.'
	USER_INVALID = 'Invalid user'
	USER_NEED_PURCHASE_PRODUCT = 'Please purchase to sign more.'
	USER_INVALID_ACCESS_TOKEN = 'Invalid user'
	USER_INVALID_SOURCE = 'Please login with google+ or facebook account.'
	USER_RECEIVED_FREE_BET_ALREADY = 'You have received free bet already!'
	USER_CANNOT_RECEIVE_VERIFICATION_CODE = 'Your input email cannot receive verification code'

	# HANDSHAKE
	HANDSHAKE_NOT_ENOUGH_GAS = 'You\'re out of gas! Please wait while we add ETH to your account.'
	HANDSHAKE_EMPTY = 'This Handshake seems to be empty.'
	HANDSHAKE_NO_PERMISSION = 'You are not authorized to make this Handshake.'
	HANDSHAKE_NO_CONTRACT_FILE = 'Contract file not found!'
	HANDSHAKE_NOT_FOUND = 'There is something wrong with your item. Please contact admin for support.'
	HANDSHAKE_TERM_AND_VALUE_NOT_MATCH = 'Please enter a payment amount.'
	HANDSHAKE_VALUE_GREATER_THAN_0 = 'Amount should be larger > 0.'
	HANDSHAKE_AMOUNT_INVALID = 'Amount key is invalid.'
	HANDSHAKE_PUBLIC_INVALID = 'Public key is invalid.'
	HANDSHAKE_INVALID_WALLET_ADDRESS = 'Please enter a valid wallet address which exists in our system.'
	HANDSHAKE_ERROR_ANYTHING = 'You\'re out of gas! Please wait while we add ETH to your account.'
	HANDSHAKE_DESC_TOO_LONG = 'Your note is too long. It should be less than 1000 characters.'
	HANDSHAKE_NO_TYPE = 'Please choose type of handshake.'
	HANDSHAKE_INVALID_BETTING_TYPE = 'This is not betting template.'
	HANDSHAKE_CANNOT_UNINIT = 'There is an error happens or you are calling cancel too fast. Need wait for 5 minutes!'
	HANDSHAKE_CANNOT_UNINIT_FREE_BET_IN_ERC20 = 'You cannot uninit ERC20 handshake!'
	HANDSHAKE_NOT_THE_SAME_RESULT = 'Your result does not match with outcome!'
	HANDSHAKE_WITHDRAW_AFTER_DISPUTE = 'Withdraw only works after dispute time.'
	HANDSHAKE_CANNOT_REFUND = 'Cannot refund this handshake!'
	HANDSHAKE_CANNOT_DISPUTE = 'Cannot dispute this handshake!'
	HANDSHAKE_CANNOT_CREATE_FREEBET_IN_ERC20 = 'You cannot create new freebet in ERC20!'
	HANDSHAKE_CANNOT_WITHDRAW_FREEBET_IN_ERC20 = 'You cannot withdraw ERC20 handshake!'

	# SHAKER
	SHAKER_NOT_FOUND = 'Shaker not found. Please try again.'
	SHAKER_ROLLBACK_ALREADY = 'You have rollbacked already!'

	# WALLET
	WALLET_EXCEED_FREE_ETH = 'Busy day for Handshakes - we\'re out of freebies! Please try again tomorrow.'
	WALLET_RECEIVE_ETH_ALREADY = 'You can only request free Handshakes once.'
	WALLET_REJECT_FREE_ETH = 'Your account can\'t get free ETH.'

	# TOKEN
	TOKEN_NOT_FOUND = 'Token not found. Please try again.'
	TOKEN_APPROVED_ALREADY = 'Token has been approved already.'

	# CONTRACT
	CONTRACT_EMPTY_VERSION = 'There is no active contract at the moment.'
	CONTRACT_INVALID = 'Contract is invalid!'

	# SOURCE
	SOURCE_INVALID = 'Source is invalid!'
	SOURCE_APPOVED_ALREADY = 'Source has been approved already!'
	SOURCE_EXISTED_ALREADY = 'Source has been existed already!'

	# CATEGORY
	CATEGORY_INVALID = 'Category is invalid!'

	# REDEEM
	REDEEM_NOT_FOUND = 'Redeem is not found!'
	REDEEM_INVALID = 'Redeem is invalid!'

	# REFERRAL
	REFERRAL_USER_JOINED_ALREADY = 'User has joined referral program already!'


class CODE(object):
	# ERROR
	INVALID_DATA = '1000' 													
	INVALID_BET = '1001' 													
	INVALID_ADDRESS = '1002' 												
	MISSING_OFFCHAIN = '1003' 												
	INVALID_ODDS = '1004' 													
	MAXIMUM_FREE_BET = '1005' 												
	FREE_BET_UNABLE = '1060'
	CANNOT_WITHDRAW = '1006' 												
	CANNOT_ROLLBACK = '1007' 
	WATTING_TIME_FREE_BET = '1053'
	CANNOT_VERIFY_EMAIL = '1054'
	CANNOT_UNSUBSCRIBE_EMAIL = '1055'
	FILE_TOO_LARGE = '1064'
	EMAIL_ALREADY_SUBSCRIBED = '1065'

	# OUTCOME
	OUTCOME_INVALID = '1008'												
	OUTCOME_INVALID_RESULT = '1009'											
	OUTCOME_HAS_RESULT = '1010' 	
	OUTCOME_IS_REPORTING = '1048'										

	# MATCH
	MATCH_NOT_FOUND = '1011'												
	MATCH_INVALID_RESULT = '1011' 											
	MATCH_RESULT_EMPTY = '1012'												
	MATCH_CANNOT_SET_RESULT = '1013'	
	MATCH_INVALID_TIME = '1043'			
	MATCH_SOURCE_EMPTY = '1067'
	MATCH_HAS_BEEN_REVIEWED = '1061'	

	# USER
	USER_INVALID_EMAIL = '1014'												
	USER_CANNOT_REGISTRY = '1015' 											
	USER_INVALID = '1016'													
	USER_NEED_PURCHASE_PRODUCT = '1017'										
	USER_INVALID_ACCESS_TOKEN = '1018' 										
	USER_INVALID_SOURCE = '1019' 											
	USER_RECEIVED_FREE_BET_ALREADY = '1020' 	
	USER_CANNOT_RECEIVE_VERIFICATION_CODE = '1068'							

	# HANDSHAKE
	HANDSHAKE_NOT_ENOUGH_GAS = '1021'	
	HANDSHAKE_EMPTY = '1022' 												
	HANDSHAKE_NO_PERMISSION = '1023' 										
	HANDSHAKE_NO_CONTRACT_FILE = '1024' 									
	HANDSHAKE_NOT_FOUND = '1025' 											
	HANDSHAKE_TERM_AND_VALUE_NOT_MATCH = '1026' 							
	HANDSHAKE_VALUE_GREATER_THAN_0 = '1027' 								
	HANDSHAKE_AMOUNT_INVALID = '1028' 										
	HANDSHAKE_PUBLIC_INVALID = '1029' 										
	HANDSHAKE_INVALID_WALLET_ADDRESS = '1030' 								
	HANDSHAKE_ERROR_ANYTHING = '1031' 										
	HANDSHAKE_DESC_TOO_LONG = '1032' 										
	HANDSHAKE_NO_TYPE = '1033' 												
	HANDSHAKE_INVALID_BETTING_TYPE = '1034' 								
	HANDSHAKE_CANNOT_UNINIT = '1035'
	HANDSHAKE_CANNOT_UNINIT_FREE_BET_IN_ERC20 = '1058' 										
	HANDSHAKE_NOT_THE_SAME_RESULT = '1036' 									
	HANDSHAKE_WITHDRAW_AFTER_DISPUTE = '1037' 	
	HANDSHAKE_CANNOT_REFUND = '1044'
	HANDSHAKE_CANNOT_DISPUTE = '1045'
	HANDSHAKE_CANNOT_CREATE_FREEBET_IN_ERC20 = '1057'
	HANDSHAKE_CANNOT_WITHDRAW_FREEBET_IN_ERC20 = '1059'

	# SHAKER
	SHAKER_NOT_FOUND = '1038' 												
	SHAKER_ROLLBACK_ALREADY = '1039'

	# WALLET
	WALLET_EXCEED_FREE_ETH = '1040' 										
	WALLET_RECEIVE_ETH_ALREADY = '1041' 									
	WALLET_REJECT_FREE_ETH = '1042' 										

	# TOKEN
	TOKEN_NOT_FOUND = '1046'
	TOKEN_APPROVED_ALREADY = '1047'


	# CONTRACT
	CONTRACT_EMPTY_VERSION = '1048'
	CONTRACT_INVALID = '1049'
	
	# SOURCE
	SOURCE_INVALID = '1050'
	SOURCE_APPOVED_ALREADY = '1051'
	SOURCE_EXISTED_ALREADY = '1052'

	# CATEGORY
	CATEGORY_INVALID = '1056'

	# REDEEM
	REDEEM_NOT_FOUND = '1062'
	REDEEM_INVALID = '1063'

	# REFERRAL
	REFERRAL_USER_JOINED_ALREADY = '1066'