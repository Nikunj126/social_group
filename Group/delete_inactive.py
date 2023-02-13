from Database.models import *
from OPS.auth import *
from flask import Response, request
from flask_restful import Resource


class DeleteInactive(Resource):
    def post(self, group_name, admin_name):
        if is_group(group_name):
            if is_user(admin_name):
                group = group_db.objects.get(group_name=group_name)
                if admin_name == group["creator"]:
                    two_days_ago = datetime.now() - timedelta(days=2)
                    posts = posts_db.objects(group_name=group_name, date__gte=two_days_ago)
                    if posts:
                        active_users = []
                        inactive_users = []
                        post = posts_db.objects.filter(group_name=group_name, date__gte=two_days_ago)
                        j = 0
                        for item in post:
                            active_users.append(post[j]["posted_by"])
                            j = j+1
                        active_users = list(set(active_users))
                        i = 0
                        for member in group["member"]:
                            flag = 0
                            for user in active_users:
                                if member == user or member in group["admin"] or member in group["moderator"]:
                                    flag = 1
                            if flag == 0:
                                inactive_users.append(member)
                            i = i+1
                        for user in inactive_users:
                            i = 0
                            for member in group["member"]:
                                if member == user:
                                    group["member"].pop(i)
                                    group.save()
                                i = i+1
                        return "All Inactive members: {} are deleted from the group.".format(inactive_users)
                    else:
                        inactive_users = []
                        i = 0
                        for member in group["member"]:
                            if member not in group["admin"] or member not in group["moderator"]:
                                inactive_users.append(member)
                            i = i+1
                        for user in inactive_users:
                            i = 0
                            for member in group["member"]:
                                if member == user:
                                    group["member"].pop(i)
                                    group.save()
                                i = i+1
                        return "All Inactive members: {} are deleted from the group.".format(inactive_users)
                else:
                    return "You don't have access for the requested operation."
            else:
                return "{} : User not found."
        else:
            return "{} : group not found."
