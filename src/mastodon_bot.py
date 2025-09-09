from mastodon import Mastodon
import time
import random
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import json


load_dotenv()


MASTO_ACCESS_TOKEN = os.getenv('MASTO_ACCESS_TOKEN')


mastodon = Mastodon(
    access_token=MASTO_ACCESS_TOKEN,
    api_base_url='https://mastodon.social'
)

last_checked_id = None



never_follow_file = "never_follow_again.json"
try:
    with open(never_follow_file, "r") as f:
        never_follow_again = json.load(f)
except FileNotFoundError:
    never_follow_again = []


follow_timestamps_file = "follow_timestamps.json"
try:
    with open(follow_timestamps_file, "r") as f:
        follow_timestamps = {
            int(k): datetime.fromisoformat(v) 
            for k, v in json.load(f).items()
        }
except FileNotFoundError:
    follow_timestamps = {}


def save_never_follow_file():
    with open(never_follow_file, "w") as f:
        json.dump(never_follow_again, f)


def save_follow_timestamps_file():
    with open(follow_timestamps_file, "w") as f:
        json.dump({
            str(k): v.isoformat() 
            for k, v in follow_timestamps.items()
        }, f)



def get_relationship(account_id):
    try:
        relationship = mastodon.account_relationships(account_id)[0]
    except IndexError as e:
        relationship = None

    return relationship


def set_favourite(post):
    try:
        status = mastodon.status_favourite(post['id'])
        print(f"Favorited post by {post['account']['acct']}")
    except mastodon.errors.MastodonNotFoundError:
        status = None
        print(f"Skipping post by {post['account']['acct']} because not found.")
    
    return status


def follow_unfollowed_account():

    public_timeline = mastodon.timeline_public(limit=20, local=True, remote=True)

    for post in public_timeline:
        time.sleep(5)
        account_id = post['account']['id']
        acct_name = post['account']['acct']
        post_language = post.get('language', None)

        if acct_name in never_follow_again:
            print(f"Skipping {acct_name} (in never follow again list).")
            continue
                
        if post_language != 'en':
            print(f"Skipping {acct_name} (non-English post).")
            continue

        relationship = get_relationship(account_id)

        if relationship is None:
            continue

        if not relationship['following']:
            mastodon.account_follow(account_id)
            status = set_favourite(post)

            if status is None:
                continue

            follow_timestamps[account_id] = datetime.now()
            save_follow_timestamps_file()

            print(f"Followed {post['account']['acct']}.")



def favourite_followed_posts():

    global last_checked_id

    if last_checked_id:
        posts = mastodon.timeline_home(since_id=last_checked_id)
    else:
        posts = mastodon.timeline_home(limit=20)

    if not posts:
        return

    for post in posts:

        acct_name = post['account']['acct']
        post_language = post.get('language', None)

        if post_language != 'en':
            print(f"Skipping {acct_name} (non-English post).")
            continue

        time.sleep(5)
        if random.random() < 0.7:
            status = set_favourite(post)

            if status is None:
                continue

    last_checked_id = posts[0]['id']



def check_unreciprocated_follows():

    global follow_timestamps

    following_accounts = mastodon.account_following(mastodon.me()['id'], limit=100)

    for account in following_accounts:
        account_id = account['id']
        acct_name = account['acct']

        relationship = get_relationship(account_id)
        
        if relationship is None:
            continue

        if not relationship['followed_by']:
            if account_id in follow_timestamps:
                followed_since = follow_timestamps[account_id]
                time_since_followed = datetime.now() - followed_since
                days_since_followed = time_since_followed.days

                if days_since_followed >= 1:
                    mastodon.account_unfollow(account_id)
                    print(f"Unfollowed {acct_name} who didn't follow back in 7 days.")

                    never_follow_again.append(acct_name)
                    save_never_follow_file()

                    del follow_timestamps[account_id]
                    save_follow_timestamps_file()

            else:
                follow_timestamps[account_id] = datetime.now()
                save_follow_timestamps_file() 
                print(f"You're following {acct_name} who does not follow you back. Tracking follow time starting from now.")



def unfollow_inactive_or_unreciprocated():
    # Get the list of accounts you're following
    following_accounts = mastodon.account_following(mastodon.me()['id'], limit=180)

    # Iterate over each account you're following
    for account in following_accounts:
        account_id = account['id']
        acct_name = account['acct']

        relationship = get_relationship(account_id)
        
        if relationship is None:
            continue

        # If they are following you back, skip this account
        if relationship['followed_by']:
            print(f"{acct_name} follows you back, skipping.")
            continue

        # Fetch their recent statuses (posts)
        statuses = mastodon.account_statuses(account_id, limit=1)

        # If they haven't posted, we can't determine activity, skip them
        if not statuses:
            print(f"{acct_name} has no posts, skipping.")
            continue

        # Get the time of their latest post
        latest_post_time = statuses[0]['created_at']

        # Check if the latest post was made within the last 24 hours
        if latest_post_time >= datetime.now(timezone.utc) - timedelta(days=1):
            # Unfollow the account if they haven't followed back and are recently active
            mastodon.account_unfollow(account_id)
            print(f"Unfollowed {acct_name} who hasn't followed back and was active in the last 24 hours.")

            never_follow_again.append(acct_name)
            save_never_follow_file()

            try:
                del follow_timestamps[account_id]
            except KeyError as e:
                pass
            save_follow_timestamps_file()
        else:
            print(f"{acct_name} wasn't active in the last 24 hours, skipping.")




# while True:
#     follow_unfollowed_account()
#     favourite_followed_posts()
#     check_unreciprocated_follows()
#     time.sleep(120)

unfollow_inactive_or_unreciprocated()

