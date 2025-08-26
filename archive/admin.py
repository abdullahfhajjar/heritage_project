from django.contrib import admin
from .models import (
    HeritageObject,
    HeritageLike,
    Comment,
    CommentLike,
    EditProposal,
    Submission,
    UserProfile,  # <-- correct name (not "Profile")
)


@admin.register(HeritageObject)
class HeritageObjectAdmin(admin.ModelAdmin):
    list_display = ("title", "title_ar", "title_fr", "region", "object_type", "origin_date")
    list_filter = ("region", "object_type", "ich_domain")
    search_fields = (
        "title", "title_ar", "title_fr", "description", "description_ar", "description_fr",
        "alternate_name", "maker", "attribution", "copy_after", "sitter",
        "period", "origin_place",
        "provenance", "collector", "site_name", "field_identifier",
        "materials", "dimensions", "weight", "taxon",
        "collection_name", "on_view_location", "exhibition_history",
        "credit_line", "data_source", "rights",
        "accession_number", "object_number", "record_id", "metadata_usage",
        "guid", "related_resource",
    )
    save_on_top = True

    fieldsets = (
        ("Core", {
            "fields": (
                "title", "title_ar", "title_fr",
                "description", "description_ar", "description_fr", 
                "region",
                "object_type",
                "ich_domain",
                ("origin_date", "date_text"),
                "image",
                "model_3d",
            )
        }),
        ("Identification (optional)", {
            "classes": ("collapse",),
            "fields": ("alternate_name", "maker", "attribution", "copy_after", "sitter",
                       "period", "origin_place"),
        }),
        ("Provenance & Collecting (optional)", {
            "classes": ("collapse",),
            "fields": ("provenance", "collector", "site_name", "field_identifier"),
        }),
        ("Materials & Measurements (optional)", {
            "classes": ("collapse",),
            "fields": ("materials", "dimensions", "weight", "taxon"),
        }),
        ("Collection & Display (optional)", {
            "classes": ("collapse",),
            "fields": ("collection_name", "on_view_location", "exhibition_history"),
        }),
        ("Source, Rights & Identifiers (optional)", {
            "classes": ("collapse",),
            "fields": ("credit_line", "data_source", "rights",
                       "accession_number", "object_number", "record_id", "metadata_usage",
                       "guid", "related_resource"),
        }),
    )

    class Media:
        # keep your custom admin CSS (safe to leave even if file doesn't exist yet)
        css = {"all": ("admin/custom-v2.css",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "object", "short_body", "is_deleted", "created_at")
    list_filter = ("is_deleted", "created_at")
    search_fields = ("body", "user__username", "user__email", "object__title")
    raw_id_fields = ("user", "object")
    date_hierarchy = "created_at"

    def short_body(self, obj):
        return (obj.body[:60] + "…") if len(obj.body) > 60 else obj.body
    short_body.short_description = "Comment"


@admin.register(HeritageLike)
class HeritageLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "object", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "object__title")
    raw_id_fields = ("user", "object")
    date_hierarchy = "created_at"


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "comment", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "comment__body")
    raw_id_fields = ("user", "comment")
    date_hierarchy = "created_at"


@admin.register(EditProposal)
class EditProposalAdmin(admin.ModelAdmin):
    list_display = ("user", "object", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "object__title", "note")
    raw_id_fields = ("user", "object")
    date_hierarchy = "created_at"


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "status", "created_at")
    list_filter = ("status", "created_at", "region", "object_type", "ich_domain")
    search_fields = ("title", "description", "user__username", "user__email")
    raw_id_fields = ("user",)
    date_hierarchy = "created_at"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "rank", "created_at")
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user",)