from OPS.mail import *
from flask_jwt_extended import jwt_required, get_jwt_identity


class CreatePost(Resource):
    @jwt_required()
    def post(self, group_name):
        posted_by = get_jwt_identity()
        body = request.get_json()
        body["group_name"] = group_name
        member_check, result = is_member(group_name, posted_by, "member")
        if member_check:
            group = group_db.objects.get(group_name=group_name)
            body["type"] = group["type"]
            create_post = posts_db(**body).save()
            post_id = create_post.id
            content = "Your post : {} was successfully created.".format(post_id)
            MailToUser(posted_by, post_id, content)
            note = ["{} created a post: {} in group {}. Please Approve.".format(posted_by, post_id, group_name)]
            MailToAdmins(group_name, note)
            return {"Post is successfully added."
                    "Post ID is: ": str(post_id)}
        else:
            return result


class ViewGroupPosts(Resource):
    @jwt_required()
    def get(self, group_name):
        user_name = get_jwt_identity()
        if is_group(group_name):
            group = group_db.objects.get(group_name=group_name)
            if is_user(user_name):
                if group["type"] == "PRIVATE":
                    member, result = is_member(group_name, user_name, "member")
                    if member:
                        posts = posts_db.objects(group_name=group_name, status="APPROVED").only("posted_by", "post")
                        if not posts:
                            return "No posts to view here!!"
                        else:
                            post = posts_db.objects(group_name=group_name, status="APPROVED").only("posted_by",
                                                                                                   "post").to_json()
                            return Response(post, mimetype="application/json", status=200)
                    elif not member and result == "{} : Not found in members of the group.".format(user_name):
                        return "{} : PRIVATE GROUP!! You don't have access to view content.".format(group_name)
                    elif not member:
                        return result
                else:
                    posts = posts_db.objects(group_name=group_name, status="APPROVED").only("posted_by", "post")
                    if not posts:
                        return "No posts to view here!!"
                    else:
                        post = posts_db.objects(group_name=group_name, status="APPROVED").only("posted_by",
                                                                                               "post").to_json()
                        return Response(post, mimetype="application/json", status=200)
            else:
                return "{} : User not found.".format(user_name)
        else:
            return "{} : Group not found.".format(group_name)


class ApprovePost(Resource):
    @jwt_required()
    def post(self, group_name, post_id, action):
        admin_name = get_jwt_identity()
        req_role_type = ["admin", "moderator"]
        access, result = has_access(group_name, admin_name, req_role_type)
        if access:
            post_check, res = is_post(group_name, post_id, "IN-TRANSIT")
            if post_check:
                if action == "DELETE":
                    post = posts_db.objects.get(id=post_id)
                    posted_by = post["posted_by"]
                    posts_db.objects.get(id=post_id).delete()
                    note = "{} {}D a post: {} in group {}.".format(admin_name, action, post_id,
                                                                                   group_name)
                    MailToAdmins(group_name, note)
                    content = "Your post was not approved by {} and was deleted.".format(admin_name)
                    MailToUser(posted_by, post_id, content)
                    return "Post deleted successfully."
                elif action == "APPROVE":
                    post = posts_db.objects.get(id=post_id)
                    post["status"] = "APPROVED"
                    content = "Your post : {} was approved by {}.".format(post_id, admin_name)
                    MailToUser(post["posted_by"], post_id, content)
                    post.save()
                    note = "{} {}D a post: {} in group {}".format(admin_name, action, post_id,
                                                                                   group_name)
                    MailToAdmins(group_name, note)
                    return "The post is approved."
                else:
                    return "Please enter correct action. Action can be only from [DELETE, APPROVE]"
            else:
                return res
        else:
            return result


class EditDeletePost(Resource):
    @jwt_required()
    def post(self, group_name):
        admin_name = get_jwt_identity()
        body = request.get_json()
        post_id = body["post_id"]
        action = body["action"]
        updated_post = body["updated_post"]
        post_check, result = is_post(group_name, post_id, "APPROVED")
        admin_check, res = is_member(group_name, admin_name, "admin")
        moderator_check, res = is_member(group_name, admin_name, "moderator")
        member_check, res = is_member(group_name, admin_name, "member")
        if post_check:
            if action == "DELETE":
                if admin_check or moderator_check:
                    post = posts_db.objects.get(id=post_id)
                    posted_by = post["posted_by"]
                    posts_db.objects.get(id=post_id).delete()
                    content = "Your post : {} was deleted by {}.".format(post_id, admin_name)
                    MailToUser(posted_by, post_id, content)
                    post.save()
                    note = "{} deleted a post: {} in group {}".format(admin_name, post_id, group_name)
                    MailToAdmins(group_name, note)
                    return "Post is successfully deleted."
                elif not admin_check and not moderator_check and member_check:
                    post = posts_db.objects(id=post_id, posted_by=admin_name)
                    if post:
                        posts_db.objects.get(id=post_id, posted_by=admin_name).delete()
                        content = "Your post : {} was successfully deleted.".format(post_id)
                        MailToUser(post["posted_by"], post_id, content)
                        post.save()
                        note = "{} deleted a post: {} in group {}".format(admin_name, post_id, group_name)
                        MailToAdmins(group_name, note)
                        return "Post is successfully deleted."
                    else:
                        return "No such post found in your group."
                else:
                    return "You don't have access for the requested operation."
            elif action == "EDIT":
                if admin_check or moderator_check:
                    post = posts_db.objects.get(id=post_id)
                    post["post"] = updated_post
                    post.save()
                    content = "Your post : {} was edited by {}.".format(post_id, admin_name)
                    MailToUser(post["posted_by"], post_id, content)
                    note = "{} edited a post: {} in group {}".format(admin_name, post_id, group_name)
                    MailToAdmins(group_name, note)
                    return "Post has been updated successfully."
                elif not admin_check and not moderator_check and member_check:
                    post = posts_db.objects(id=post_id, posted_by=admin_name)
                    if post:
                        post["post"] = updated_post
                        post["status"] = "IN-TRANSIT"
                        content = "Your post : {} was successfully edited.".format(post_id)
                        MailToUser(post["posted_by"], post_id, content)
                        note = "{} edited a post: {} in group {}. Please approve.".format(admin_name, post_id, group_name)
                        MailToAdmins(group_name, note)
                    else:
                        return "You can only edit your post!!"
                else:
                    return "You don't have access for the requested operation."
            else:
                return "Please enter the correct action. Action can be only from [DELETE, EDIT]."
        else:
            return result

