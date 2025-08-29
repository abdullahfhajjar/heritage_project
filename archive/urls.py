from django.urls import path
from . import views

urlpatterns = [
    # 🏠 Homepage
    path("", views.home, name="home"),
    
    # 🔐 Authentication
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),

    # 📚 Collections / listing
    path("heritage/", views.heritage_list, name="heritage-list"),
    path("filter/", views.heritage_filtered, name="heritage-filtered"),

    # 📜 Individual heritage object detail
    path("heritage/<int:pk>/", views.heritage_detail, name="heritage-detail"),

    # ❤️ Object likes
    path("heritage/<int:pk>/like/", views.toggle_like, name="heritage-like"),
    path("heritage/<int:pk>/like/", views.toggle_like, name="toggle-like"),  # alias

    # 💬 Comments
    path("heritage/<int:pk>/comment/", views.post_comment, name="post-comment"),
    path("heritage/<int:pk>/comment/", views.post_comment, name="comment-create"),  # alias

    # Comment likes (this is the one the template needs)
    path("comment/<int:comment_id>/like/", views.toggle_comment_like, name="comment-like"),
    path("comment/<int:comment_id>/like/", views.toggle_comment_like, name="toggle-comment-like"),  # alias
    
    # Comment replies
    path("comment/<int:comment_id>/reply/", views.post_comment_reply, name="comment-reply"),

    # Comment delete
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="comment-delete"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete-comment"),  # alias

    # ✍️ Propose edits to existing objects
    path("heritage/<int:pk>/propose-edit/", views.propose_edit, name="propose-edit"),
    path("heritage/<int:pk>/propose-edit-inline/", views.propose_edit_inline, name="propose-edit-inline"),

    # 📥 Community submissions (new objects)
    path("submit/", views.submit_object, name="submit-object"),
    path("my/submissions/", views.my_submissions, name="my-submissions"),
    path("my/proposals/", views.my_proposals, name="my-proposals"),

    # 👤 Profiles
    path("me/", views.me_dashboard, name="me-dashboard"),
    path("u/<str:username>/", views.public_profile, name="public-profile"),

    # ℹ️ Static pages
    path("about/", views.about, name="about"),
    path("sponsors/", views.sponsors, name="sponsors"),
    path("donate/", views.donate, name="donate"),
]
