import data.slackarchive as slackarchive
from datetime import datetime
import re
import collections


def give_date_organised_logs(domain, channel_id, starting_date, ending_date, size, offset):
    """
    This function returns a dict og logs arranged by dates along with user details
    :param domain: The domain of the Slack team. Eg. 'kubernetes' in 'https://kubernetes.slackarchive.io/'
    :param channel_id: The unique channel identifier as returned by the fetch_channel function.
    :param starting_date: The starting date (date-time object) for analysis
    :param ending_date: The ending date (date-time object) for analysis
    :param size: The number of messages to fetch, in a reverse-chronological order.
    :param offset: The number of messages to skip while fetching, in a reverse-chronological order. An
    offset of 5 with a size of 100 will fetch the 100 messages after the 5 latest messages in a channel.
    :return: logs - dict arranged by dates, user_info - information about the users in the logs
    """
    logs = collections.defaultdict(list)
    team_data = slackarchive.fetch_team(domain)
    messages_data = slackarchive.fetch_messages(domain, team_data["team_id"], channel_id, size, offset)
     
    messages = messages_data["messages"]
    related = messages_data["related"]
    user_info = related["users"]

    for message_dict in messages:
        message_type = message_dict["type"]
        message_sender = message_dict["user"]
        raw_message_text = message_dict["text"]
        tagged_users = re.findall(r'<@(\S+)>', raw_message_text)
        unixtimestamp = float(message_dict["ts"])
        
        """
            Formats of text stripped from raw string:
            tagged_user = <@userID>
            emoticon = :grin_face:
            link = <weblink>
            code = `code`
        """
        processed_message_text = " ".join(re.sub(r'<@(\S+)>|:(\S+):|<(\S+)>|`(.*)`', '', raw_message_text).strip().split())

        if message_type == "message":
            datetimestamp = datetime.fromtimestamp(unixtimestamp)
            if starting_date <= datetimestamp <= ending_date:
                logs[datetimestamp].append({
                    "raw_text": raw_message_text,
                    "processed_text": processed_message_text,
                    "sender": message_sender,
                    "receiver": tagged_users,
                })
            else:
                #TODO
                pass

    return logs, user_info        


starting_date = datetime.strptime("1-1-2017", "%d-%m-%Y")
ending_date = datetime.strptime("25-12-2017", "%d-%m-%Y")
logs, user_info = give_date_organised_logs("kubernetes", "C4YCQ57CG", starting_date, ending_date, 1000, 0)