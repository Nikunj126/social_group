from flask import Response, request
from flask_restful import Resource
from OPS.mail import *


class CommentPost(Resource):
    def post(self, group_name):
        body = request.get_json()
        user_name = body["user_name"]
        post_id = body["post_id"]
        body["group_name"] = group_name
        if is_group(group_name):
            post_check, res2 = is_post(group_name, post_id, "APPROVED")
            post2 = posts_db.objects.get(id=post_id)
            body["post_of"] = post2["posted_by"]
            if post_check:
                group = group_db.objects.get(group_name=group_name)
                if is_user(user_name):
                    if group["type"] == "PRIVATE":
                        member, result = is_member(group_name, user_name, "member")
                        if member:
                            posts = posts_db.objects(id=post_id, group_name=group_name, status="APPROVED")
                            if not posts:
                                return "No posts to view here!!"
                            else:
                                comment = comment_db(**body).save()
                                comment_id = comment.id
                                post1 = posts_db.objects.get(group_name=group_name, id=post_id)
                                content = "{} commented on your post: {}".format(user_name, post_id)
                                MailToUser(post1["posted_by"], post_id, content)
                                note = "{} commented on a post: {} in group {}".format(user_name, post_id, group_name)
                                MailToAdmins(group_name, note)
                                return "Your comment id : {}".format(comment_id)
                        elif not member and result == "{} : Not found in members of the group.".format(user_name):
                            return "{} : PRIVATE GROUP!! You don't have access to comment.".format(group_name)
                        elif not member:
                            return result
                    else:
                        posts = posts_db.objects(id=post_id, group_name=group_name, status="APPROVED")
                        if not posts:
                            return "No posts to view here!!"
                        else:
                            comment = comment_db(**body).save()
                            comment_id = comment.id
                            post1 = posts_db.objects.get(group_name=group_name, id=post_id)
                            content = "{} commented on your post: {}".format(user_name, post_id)
                            MailToUser(post1["posted_by"], post_id, content)
                            note = "{} commented on a post: {} in group {}".format(user_name, post_id, group_name)
                            MailToAdmins(group_name, note)
                            return "Your comment id : {}".format(comment_id)
                else:
                    return "{} : User not found.".format(user_name)
            else:
                return res2
        else:
            return "{} : Group not found.".format(group_name)


class EditDeleteComment(Resource):
    def post(self, group_name, post_id):
        body = request.get_json()
        user_name = body["user_name"]
        comment_id = body["comment_id"]
        action = body["action"]
        updated_comment = body["updated_comment"]
        admin_check, res = is_member(group_name, user_name, "admin")
        moderator_check, res = is_member(group_name, user_name, "moderator")
        if is_group(group_name):
            if is_user(user_name):
                comment_check, result = is_comment(post_id, comment_id)
                if comment_check:
                    if action == "DELETE":
                        comments = comment_db.objects.get(id=comment_id)
                        post = posts_db.objects.get(id=post_id)
                        post1 = posts_db.objects.get(group_name=group_name, id=post_id)
                        content = "{} deleted a comment on your post: {}".format(user_name, post_id)
                        MailToUser(post1["posted_by"], post_id, content)
                        note = "{} deleted a commented on post: {} in group {}".format(user_name, post_id, group_name)
                        MailToAdmins(group_name, note)
                        if admin_check or moderator_check:
                            comment_db.objects.get(id=comment_id, post_id=post_id).delete()
                            return "comment : {} has been edited successfully.".format(comment_id)
                        elif comments["user_name"] == user_name:
                            comment = comment_db.objects(id=comment_id, post_id=post_id).delete()
                            return "comment : {} has been deleted successfully.".format(comment_id)
                        elif post["posted_by"] == user_name:
                            comment = comment_db.objects(id=comment_id, post_id=post_id).delete()
                            return "comment : {} has been deleted successfully.".format(comment_id)
                        else:
                            return "You don't have access to delete given comment."
                    if action == "EDIT":
                        comments = comment_db.objects.get(id=comment_id)
                        post = posts_db.objects.get(id=post_id)
                        if admin_check or moderator_check:
                            comment = comment_db.objects.get(id=comment_id, post_id=post_id)
                            comment["comment"] = updated_comment
                            comment.save()
                            post1 = posts_db.objects.get(group_name=group_name, id=post_id)
                            content = "{} edited a comment on your post: {}".format(user_name, post_id)
                            MailToUser(post1["posted_by"], post_id, content)
                            note = "{} edited a comment on a post: {} in group {}".format(user_name, post_id,
                                                                                          group_name)
                            MailToAdmins(group_name, note)
                            return "comment : {} has been edited successfully.".format(comment_id)
                        elif comments["user_name"] == user_name:
                            comment = comment_db.objects.get(id=comment_id, post_id=post_id)
                            comment["comment"] = updated_comment
                            comment.save()
                            post1 = posts_db.objects.get(group_name=group_name, id=post_id)
                            content = "{} edited a comment on your post: {}".format(user_name, post_id)
                            MailToUser(post1["posted_by"], post_id, content)
                            note = "{} edited a comment on a post: {} in group {}".format(user_name, post_id,
                                                                                          group_name)
                            MailToAdmins(group_name, note)
                            return "comment : {} has been edited successfully.".format(comment_id)
                        elif post["posted_by"] == user_name:
                            comment = comment_db.objects.get(id=comment_id, post_id=post_id)
                            comment["comment"] = updated_comment
                            comment.save()
                            post1 = posts_db.objects.get(group_name=group_name, id=post_id)
                            content = "{} edited a comment on your post: {}".format(user_name, post_id)
                            MailToUser(post1["posted_by"], post_id, content)
                            note = "{} edited a comment on a post: {} in group {}".format(user_name, post_id,
                                                                                          group_name)
                            MailToAdmins(group_name, note)
                            return "comment : {} has been edited successfully.".format(comment_id)
                        else:
                            return "You don't have access to edit given comment."
                    else:
                        return "Please enter the correct action. Action can be only from [DELETE, EDIT]."
                else:
                    return result
            else:
                return "{} : User not found.".format(user_name)
        else:
            return "{} : Group not found.".format(group_name)
