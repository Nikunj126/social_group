from OPS.sign_up import *
from Group.group_ops import *
from Post.post_ops import *
from Comment.comment_ops import *
from Group.delete_inactive import *



def initialize_routes(api):
    api.add_resource(SignUp, "/user/signup")
    api.add_resource(LogIn, "/user/login")
    api.add_resource(CreateGroup, "/group/create")
    api.add_resource(DeleteGroup, "/group/delete")
    api.add_resource(AddMember, "/group/add/member")
    api.add_resource(RemoveRole, "/group/remove/<role>")
    api.add_resource(AddRole, "/group/add/<role>")
    api.add_resource(RemoveMember, "/group/remove/member")
    api.add_resource(CreatePost, "/<group_name>/post")
    api.add_resource(ViewGroupPosts, "/<group_name>/post/view/all")
    api.add_resource(ApprovePost, "/approve&delete&post/<group_name>/<post_id>/<action>")
    api.add_resource(EditDeletePost, "/edit&delete&post/<group_name>")
    api.add_resource(CommentPost, "/comment&post/<group_name>")
    api.add_resource(EditDeleteComment, "/edit&delete&comment/<group_name>/<post_id>")
    api.add_resource(DeleteInactive, "/delete/inactive/<group_name>")
