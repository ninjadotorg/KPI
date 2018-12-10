#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
import time
import app.constants as CONST

from app.models import Match
from datetime import datetime
from app.helpers.utils import render_unsubscribe_url, second_to_strftime, render_generate_link
from app.constants import Handshake as HandshakeStatus

def render_email_subscribe_content(match_id):
    return """
        Hey Ninja!<br/><br/>
        You’ve successfully made a prediction: <br/><br/>
        {}
        Great work! We’ll email you the result as soon as it’s been reported.<br/><br/>
        Enjoy daydreaming about all of the things you’ll (hopefully) do with your winnings.<br/><br/>
        Stay cool.<br/><br/>
        {}
    """.format(render_match_content(match_id), render_signature_content())


def render_email_claim_redeem_code_content(redeem_code_1, redeem_code_2, referral_link):
    return """
        Hey Ninja!<br/><br/>
        Welcome to our platform, it’s great to see you!<br/>
        Please use the following redeem codes to claim your free predictions: <br/><br/>
        <b>Code 1:</b> {}  (0.03ETH)<br/>
        <b>Code 2:</b> {}  (0.03ETH)<br/><br/>
        Just redeem the code on the bet screen and you're good to go!.<br/><br/>
        You can earn additional free predictions for every friend you refer to our platform.<br/>
        How? It’s easy, just share this link with them (<a>{}</a>)!<br/><br/>
        You look like a winner!<br/><br/>
        {}
    """.format(redeem_code_1, redeem_code_2, referral_link, render_signature_content())


def render_result_email_content(match_name, outcome_result, user_choice):
    return """
        Hey Ninja,<br/><br/>
        {}
        <br/>
        {}
    """.format(render_event_result(match_name, outcome_result, user_choice), render_signature_content())


def render_reward_email_content(redeem_code, referral_link):
    return """
        Hey Ninja!<br/><br/>
        A friend you referred to us has joined the platform!<br/>
        Thanks for that! Here’s your reward: <br/><br/>
        <b>Code:</b> {}  (0.03ETH)<br/><br/>
        Just redeem the code on the bet screen and you're good to go!.<br/><br/>
        Remember; you can earn additional free predictions for every friend you refer to our platform.<br/>
        How? It’s easy, just share this link with them (<a>{}</a>)!<br/><br/>
        You look like a winner!<br/><br/>
        {}
    """.format(redeem_code, referral_link, render_signature_content())


def render_renew_redeem_email_content(redeem_code, referral_link):
    return """
        Hey Ninja!<br/><br/>
        Here’s your new redeem code: <br/><br/>
        <b>Code:</b> {}  (0.03ETH)<br/><br/>
        Just redeem the code on the bet screen and you're good to go!.<br/><br/>
        Remember; you can earn additional free predictions for every friend you refer to our platform.<br/>
        How? It’s easy, just share this link with them (<a>{}</a>)!<br/><br/>
        You look like a winner!<br/><br/>
        {}
    """.format(redeem_code, referral_link, render_signature_content())


def render_event_result(match_name, outcome_result, user_choice):
    if outcome_result == CONST.RESULT_TYPE['DRAW']:
        return render_event_not_happen_content(match_name)
    
    elif outcome_result == user_choice:
        return render_choose_correct_side_content(match_name, user_choice)
    
    else:
        return render_choose_wrong_side_content(match_name, user_choice)


def render_event_not_happen_content(match_name):
    return """
        <font style="font-size:20px"> Sorry... </font><br/>
        The event {} did not go ahead as scheduled. Our apologies for this; we’ll make sure your wager is refunded and will appear on the ‘Me’ page.<br/><br/>
        If you have any questions, please get in touch with us on <a href="http://t.me/ninja_org">Telegram</a> or contact <a href="mailto:support@ninja.org">support@ninja.org</a>.<br/><br/>
        Don’t worry, there are plenty of other predictions to make: <br/><br/>
        Play NOW at <a href="http://www.ninja.org/pex">http://www.ninja.org/pex</a> on your mobile, <br/>
        Or why not try your hand at creating a market? <a href="https://ninja.org/create-pex">https://ninja.org/create-pex</a><br/>
    """.format(match_name, 'YES' if user_choice == 1 else 'NO')


def render_choose_correct_side_content(match_name, user_choice):
    return """
        The results are in, so let’s see how you did… <br/><br/>
        <font style="font-size:20px"> Congratulations! </font><br/>
        You correctly predicted {} With the result being {}. <br/>
        Nice work! You’re on a roll... what will you predict next? <br/>
        Check out the available markets NOW at <a href="http://www.ninja.org/pex">http://www.ninja.org/pex</a> on your mobile!<br/>
    """.format(match_name, 'YES' if user_choice == 1 else 'NO')


def render_choose_wrong_side_content(match_name, user_choice):
    return """
        The results are in, so let’s see how you did… <br/><br/>
        <font style="font-size:20px"> Bad luck... </font><br/>
        The event {} closed and the result was {}, but you predicted {}. Sorry but this time, your prediction was wrong.  <br/>
        Don’t worry, there are plenty of other predictions to make: <br/><br/>
        Play NOW at <a href="http://www.ninja.org/pex">http://www.ninja.org/pex</a> on your mobile, <br/>
        Or why not try your hand at creating a market? <a href="https://ninja.org/create-pex">https://ninja.org/create-pex</a><br/>

    """.format(match_name, 'YES' if user_choice == 2 else 'NO', 'YES' if user_choice == 1 else 'NO')


def render_verification_success_mail_content(base_url, match_id, uid, referral_link):
    return """
        Hey Ninja,<br/><br/>
        Good news!!! <br/>
        Your event (below) has been verified and will now appear on the exchange! <br/><br/>
        {}
        <b>Invite your friends to bet on this market by sharing the direct link below:</b><br/>
        {}<br/><br/>
        You can also earn additional free predictions for every friend you refer to our platform.<br/>
        How? It’s easy, just share this link with them ({})!<br/><br/>
        If you have any questions, please get in touch with us on <a href="http://t.me/ninja_org">Telegram</a> or contact <a href="mailto:support@ninja.org">support@ninja.org</a>.<br/><br/>
        Good luck!<br/>
        {}
    """.format(render_match_content(match_id), "{}prediction/{}".format(base_url, render_generate_link(match_id, uid)), referral_link, render_signature_content())


def render_verification_failed_mail_content(match_id):
    return """
        Hey Ninja,<br/><br/>
        There was an issue with the below event and we weren’t able to list it on the exchange. <br/>
        {}
        If you have any questions, please get in touch with us on <a href="http://t.me/ninja_org">Telegram</a> or contact <a href="mailto:support@ninja.org">support@ninja.org</a>.<br/><br/>
        Good luck!<br/>
        {}
    """.format(render_match_content(match_id), render_signature_content())


def render_create_new_market_mail_content(match_id):
    return """
        Hey Ninja,<br/><br/>
        Congratulations; your event was created successfully!  <br/>
        We’ll send you an email shortly to let you know if your market was approved, before adding it to the exchange. <br/>
        <b>Note:</b> Due to the approval process, it can take up to one hour for new events to appear on the exchange. <br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;In the meantime, please review the event details below: <br/><br/>
        {}
        If you have any questions, please get in touch with us on <a href="http://t.me/ninja_org">Telegram</a> or contact <a href="mailto:support@ninja.org">support@ninja.org</a>.<br/><br/>
        Good luck!<br/>
        {}
    """.format(render_match_content(match_id), render_signature_content())


def render_signature_content():
    return """
        Ninja.org<br/>
        Join us on Telegram: <a href="http://t.me/ninja_org">http://t.me/ninja_org</a><br/>
        <div>
            <span style="">Find us on </span>
            <a href="https://www.facebook.com/ninjadotorg"><img height="30" width="30" style="vertical-align:middle" src="https://storage.googleapis.com/cryptosign/images/email_flows/facbook.png" alt="Facebook"></a>
            <a href="https://twitter.com/ninjadotorg"><img height="30" width="30" style="vertical-align:middle" src="https://storage.googleapis.com/cryptosign/images/email_flows/twitter.png" alt="Twitter"></a>
        </div>
    """


def render_match_content(match_id):
    match = Match.find_match_by_id(match_id)
    closing_time = second_to_strftime(match.date) 
    report_time = second_to_strftime(match.reportTime)
    dispute_time = second_to_strftime(match.disputeTime)
    return """
        <div>
            <blockquote style="margin:0 0 15px 15px;border:none;padding:0px">
                <div>
                    <b>Event name:</b> {}<br/>
                    <b>Your event ends:</b> {} (UTC)<br/>
                    <b>Report results before:</b> {} (UTC)<br/>
                    <b>Event closes:</b> {} (UTC) (if there’s no dispute)<br/>
                </div>
            </blockquote>
        </div>
    """.format(match.name, closing_time, report_time, dispute_time)