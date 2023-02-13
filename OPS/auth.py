from Database.models import *


def is_user(user_name_input):
    user = user_db.objects(user_name=user_name_input)
    if user:
        return True
    else:
        return False


def is_group(group_name_input):
    user = group_db.objects(group_name=group_name_input)
    if user:
        return True
    else:
        return False


def is_member(group_name, user_name, role):
    if is_group(group_name):
        if is_user(user_name):
            if role in ["admin", "member", "moderator"]:
                roles = group_db.objects.get(group_name=group_name)
                flag = 0
                result = ""
                for name in roles[role]:
                    if name == user_name:
                        flag = 1

                if flag == 1:
                    return True, result
                else:
                    return False, "{} : Not found in {}s of the group.".format(user_name, role)
            else:
                return False, "{} : Role not Valid. Role can be only from [admin, moderator, member]".format(role)
        else:
            return False, "{} : User not found.".format(user_name)
    else:
        return False, "{} : Group not found.".format(group_name)


def are_user(members):
    missing = []
    present = []
    flag = 1
    for item in members:
        user = user_db.objects(user_name=item)
        if user:
            present.append(item)
        else:
            missing.append(item)
            flag = 0
    if flag == 1:
        return True, missing, present
    else:
        return False, missing, present


def has_access(group_name, user_name, req_role_type):
    flag = 0
    if is_group(group_name):
        if is_user(user_name):
            group = group_db.objects.get(group_name=group_name)
            for item in req_role_type:
                if item == "creator":
                    if user_name == group["creator"]:
                        flag = 1
                else:
                    for name in group[item]:
                        if name == user_name:
                            flag = 1
            if flag == 1:
                return True, ""
            else:
                return False, "You don't have access for the requested operation."
        else:
            return False, "{} : User not found.".format(user_name)
    else:
        return False, "{} : Group not found.".format(group_name)


def are_missing(group_name, user_name, role):
    missing = []
    present = []
    roles = group_db.objects.get(group_name=group_name)
    for name in user_name:
        flag = 0
        for item in roles[role]:
            if name == item:
                flag = 1
            else:
                continue
        if flag == 0:
            missing.append(name)
        elif flag == 1:
            present.append(name)
    if not present:
        return True, missing, present
    if present:
        return False, missing, present


def is_post(group_name, post_id, status):
    result = ""
    posts = posts_db.objects(id=post_id)
    if posts:
        if is_group(group_name):
            post = posts_db.objects(group_name=group_name, id=post_id, status=status)
            if post:
                return True, result
            else:
                return False, "No such post found in the group!!"
        else:
            return "{} : Group not found.".format(group_name)
    else:
        return False, "No post found with the given post_id!!"


def is_comment(post_id, comment_id):
    posts = posts_db.objects(id=post_id, status="APPROVED")
    comment_on_post = comment_db.objects(id=comment_id, post_id=post_id)
    if posts:
        if comment_on_post:
            return True, ""
        else:
            return False, "{} : Comment not found on the given post.".format(comment_id)
    else:
        return False, "No post found with the given post_id!!"


def is_notification(group_name, note):
    today = date.today()
    notification = notification_db.objects(group_name=group_name, note_date=today)
    if notification:
        notifications = notification_db.objects.get(group_name=group_name, note_date=today)
        notifications["notification"].append(note[0])
        notifications.save()
    else:
        body = {"group_name": group_name, "note_date": today, "notification": note}
        notification_db(**body).save()


def body(notifications):
    content = ""
    i = 0
    for item in notifications:
        content = content + "{}. {}\n".format(i+1, notifications[i])
        i = i+1
    return content

