from OPS.mail import *
from flask_jwt_extended import jwt_required, get_jwt_identity


class CreateGroup(Resource):
    @jwt_required()
    def post(self):
        try:
            user_name = get_jwt_identity()
            body = request.get_json()
            body["creator"] = user_name
            group_name = body["group_name"]
            if user_name in body["admin"]:
                pass
            else:
                body["admin"] = body["admin"] + [user_name]
            if user_name in body["moderator"]:
                pass
            else:
                body["moderator"] = body["moderator"] + [user_name]
            body["member"] = set(body["moderator"] + body["member"] + body["admin"])
            boolean, missing_member, present_member = are_user(body["member"])
            boolean1, missing_moderator, present_moderator = are_user(body["moderator"])
            boolean2, missing_admin, present_admin = are_user(body["admin"])
            if is_user(user_name):
                if body["type"] in ["PUBLIC", "PRIVATE"]:
                    if boolean:
                        group_db(**body).save()
                        content = "{} created a group: {} & added you as a admin/moderator.".format(user_name,
                                                                                                    group_name)
                        MailToAdmins(group_name, content)
                        return "Group {} is successfully created.".format(body["group_name"])
                    else:
                        body["member"] = present_member
                        body["admin"] = present_admin
                        body["moderator"] = present_moderator
                        group_db(**body).save()
                        result = "{} : USER / USERS NOT FOUND.  Group {} is created with all the other" \
                                 " users".format(str(missing_member), body["group_name"])
                        content = "{} created a group: {} & added you as a admin/moderator.".format(user_name, group_name)
                        MailToAdmins(group_name, content)
                        return result
                else:
                    return "Please enter the correct group type. It can be only from [PUBLIC, PRIVATE]."
            else:
                return "{}, you can't create a group because you are not a user.".format(user_name)
        except mongoengine.errors.NotUniqueError:
            return "Group name is already taken, please try other name."


class DeleteGroup(Resource):
    @jwt_required()
    def post(self):
        identity = get_jwt_identity()
        req_role_type = ["creator"]
        body = request.get_json()
        group_name = body["group_name"]
        user1 = user_db.objects.get(id=identity)
        user_name = user1["user_name"]
        boolean, result = has_access(group_name, user_name, req_role_type)
        if boolean:
            group_db.objects.get(group_name=group_name).delete()
            content = "{} deleted the group: {}".format(user_name, group_name)
            MailToAdmins(group_name, content)
            return 'Group: {} is successfully deleted'. format(group_name)
        else:
            return result


class AddMember(Resource):
    @jwt_required()
    def post(self):
        admin_name = get_jwt_identity()
        req_role_type = ["creator", "admin"]
        body = request.get_json()
        group_name = body["group_name"]
        user_name = body["user_name"]
        role = "member"
        boolean, result = has_access(group_name, admin_name, req_role_type)
        if boolean:
            all_user, user_not_found, user_found = are_user(user_name)
            all_missing, missing_users, present_users = are_missing(group_name, user_found, role)
            roles = group_db.objects.get(group_name=group_name)
            if all_user and all_missing:
                for item in missing_users:
                    roles[role].append(item)
                    roles.save()
                    content = "{} added {} in members of the group :{}".format(admin_name, user_name, group_name)
                    MailToAdmins(group_name, content)
                return "{} is added to the {}s of the group successfully.".format(user_name, role)
            elif not all_user and all_missing:
                for item in missing_users:
                    roles[role].append(item)
                    roles.save()
                    content = "{} added {} in members of the group :{}".format(admin_name, user_name, group_name)
                    MailToAdmins(group_name, content)
                return "{} : USER / USERS not found. All the other users are added to {}s " \
                       "successfully.".format(str(user_not_found), role)
            elif all_user and not all_missing:
                for item in missing_users:
                    roles[role].append(item)
                    roles.save()
                    content = "{} added {} in members of the group :{}".format(admin_name, user_name, group_name)
                    MailToAdmins(group_name, content)
                return "{}: USER / USERS already present as {}. " \
                       "All the other users are added to the {}s of " \
                       "the group.".format(str(present_users), role, role)
            elif not all_user and not all_missing:
                for item in missing_users:
                    roles[role].append(item)
                    roles.save()
                    content = "{} added {} in members of the group :{}".format(admin_name, user_name, group_name)
                    MailToAdmins(group_name, content)
                return "{}: USER / USERS not found." \
                       "{}: USER / USERS already present as {}." \
                       "All the other users are added to the {}s of the " \
                       "group.".format(str(user_not_found), present_users, role, role)
        else:
            return result


class AddRole(Resource):
    @jwt_required()
    def post(self, role):
        admin_name = get_jwt_identity()
        body = request.get_json()
        group_name = body["group_name"]
        user_name = body["user_name"]
        req_role_type = ["admin", "creator"]
        access_check, result = has_access(group_name, admin_name, req_role_type)
        member_check, res0 = is_member(group_name, user_name, "member")
        role_check, res = is_member(group_name, user_name, role)
        if access_check:
            if member_check:
                if role_check:
                    return "{} is already in the {}s of the group.".format(user_name, role)
                elif not role_check and res == "{} : Not found in {}s of the group.".format(user_name, role):
                    group = group_db.objects.get(group_name=group_name)
                    group[role].append(user_name)
                    group.save()
                    content = "{} added {} in {}s of the group :{}".format(admin_name, user_name, role, group_name)
                    MailToAdmins(group_name, content)
                    return "{} is added successfully in {}s of the group.".format(user_name, role)
                elif not role_check and res != "{} : Not found in {}s of the group.".format(user_name, role):
                    return res
            elif res0 == "{} : Not found in {}s of the group.".format(user_name, "member"):
                return "{} is not a member of the group. Please add as a member first.".format(user_name)
            else:
                return res0
        else:
            return result


class RemoveRole(Resource):
    @jwt_required()
    def post(self, role):
        admin_name = get_jwt_identity()
        body = request.get_json()
        group_name = body["group_name"]
        user_name = body["user_name"]
        req_role_type = ["creator"]
        access_check, result = has_access(group_name, admin_name, req_role_type)
        if access_check:
            role_check, res = is_member(group_name, user_name, role)
            if role in ["admin", "moderator"]:
                if role_check:
                    group = group_db.objects.get(group_name=group_name)
                    if user_name == group["creator"]:
                        return "Creator of the group can't be removed."
                    else:
                        i = -1
                        for name in group[role]:
                            i = i+1
                            if name == user_name:
                                group[role].pop(i)
                                group.save()
                                content = "{} removed {} from {}s of the group :{}".format(admin_name, user_name, role,
                                                                                       group_name)
                                MailToAdmins(group_name, content)
                        return "{} is successfully removed from the {}s of the group.".format(user_name, role)
                else:
                    return "{} : Not found in {}s of the group.".format(user_name, role)
            else:
                return "{} : Role not Valid. Role can be only from [admin, moderator, member]".format(role)
        else:
            return result


class RemoveMember(Resource):
    @jwt_required()
    def post(self):
        admin_name = get_jwt_identity()
        body = request.get_json()
        group_name = body["group_name"]
        user_name = body["user_name"]
        req_role_type = ["creator", "admin"]
        access_check, result = has_access(group_name, admin_name, req_role_type)
        if access_check:
            member_check, res = is_member(group_name, user_name, "member")
            if member_check:
                group = group_db.objects.get(group_name=group_name)
                if user_name != group["creator"]:
                    i = -1
                    for name in group["member"]:
                        i = i + 1
                        if name == user_name:
                            group["member"].pop(i)
                            group.save()
                            content = "{} removed {} from members of the group :{}".format(admin_name, user_name,
                                                                                     group_name)
                            MailToAdmins(group_name, content)
                        else:
                            pass
                    i = -1
                    for name in group["admin"]:
                        i = i+1
                        if name == user_name:
                            group["admin"].pop(i)
                            group.save()
                            content = "{} removed {} from members of the group :{}".format(admin_name, user_name,
                                                                                           group_name)
                            MailToAdmins(group_name, content)
                        else:
                            pass
                    i = -1
                    for name in group["moderator"]:
                        i = i + 1
                        if name == user_name:
                            group["moderator"].pop(i)
                            group.save()
                            content = "{} removed {} from members of the group :{}".format(admin_name, user_name,
                                                                                           group_name)
                            MailToAdmins(group_name, content)
                        else:
                            pass
                    return "{} is removed from the group.".format(user_name)
                else:
                    return "Creator of the group can't be removed."
            else:
                return res
        else:
            return result
