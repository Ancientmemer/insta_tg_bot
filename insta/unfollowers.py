from insta.client import cl

def get_unfollowers():
    uid = cl.user_id
    followers = set(cl.user_followers(uid).keys())
    following = set(cl.user_following(uid).keys())
    unf = following - followers
    return [cl.user_info(u).username for u in unf]
