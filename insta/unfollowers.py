from insta.client import cl

def get_unfollowers():
    user_id = cl.user_id
    followers = set(cl.user_followers(user_id).keys())
    following = set(cl.user_following(user_id).keys())

    unfollowers = following - followers
    return [cl.user_info(uid).username for uid in unfollowers]
