from twilio.rest import Client
from twilio.rest.studio.v2.flow.execution import ExecutionInstance
import os
import logging
import sys
import datetime

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    acsid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    flow_sid = os.environ.get('TWILIO_FLOW_SID')

    log = logging.getLogger('foodnow')
    log.setLevel(logging.DEBUG)

    client = Client(acsid, auth_token)
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)

    log.info("Deleting executions")
    try:
        for execution in client.studio.flows.get(flow_sid).executions.list(date_created_from=last_week):
            try:
                if execution.status != ExecutionInstance.Status.ACTIVE:
                    log.info("Delete execution {}".format(execution.sid))
                    execution.delete()
            except Exception:
                log.exception("An exception occurred deleting an execution")
    except Exception:
        log.exception("An exception occurred iterating executions")

    log.info("Deleting messages")
    try:
        for message in client.messages.list(date_sent_after=last_week):
            try:
                log.info("Delete message {}".format(message.sid))
                message.delete()
            except Exception:
                log.exception("An exception occurred deleting a message")
    except Exception:
        log.exception("An exception occurred iterating messages")

    log.info("Deleting calls")
    try:
        for call in client.calls.list(start_time_after=last_week):
            try:
                if call.status not in [call.Status.IN_PROGRESS, call.Status.RINGING, call.Status.QUEUED]:
                    log.info("Delete call {}".format(call.sid))
                    call.delete()
            except Exception:
                log.exception("An exception occurred deleting a call")
    except Exception:
        log.exception("An exception occurred iterating calls")




