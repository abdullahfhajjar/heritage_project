from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import (
    HeritageObject,
    HeritageLike,
    Comment,
    CommentLike,
    EditProposal,
    Submission,
    UserProfile,
)
from .admin_site import admin_site

# Unregister default User admin from default site
admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class EnhancedUserAdmin(BaseUserAdmin):
    """Enhanced User admin with OAuth detection and profile integration"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'auth_type_display', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    
    def auth_type_display(self, obj):
        """Show if user is using Google OAuth or regular registration"""
        if hasattr(obj, 'socialaccount_set') and obj.socialaccount_set.exists():
            providers = obj.socialaccount_set.values_list('provider', flat=True)
            if 'google' in providers:
                return format_html(
                    '<span style="background: #4285f4; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Google</span>'
                )
            else:
                return format_html(
                    '<span style="background: #6c757d; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">OAuth</span>'
                )
        return format_html(
            '<span style="background: #2C3E50; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Registered</span>'
        )
    auth_type_display.short_description = 'Auth Type'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('socialaccount_set')


@admin.register(HeritageObject, site=admin_site)
class HeritageObjectAdmin(admin.ModelAdmin):
    """Main heritage object administration with enhanced features"""
    list_display = ("title", "title_ar", "region", "object_type", "origin_date", "has_3d_model", "likes_count", "comments_count")
    list_filter = ("region", "object_type", "ich_domain")
    search_fields = (
        "title", "title_ar", "title_fr", "description", "description_ar", "description_fr",
        "alternate_name", "maker", "attribution", "origin_place",
    )
    save_on_top = True
    
    def has_3d_model(self, obj):
        """Check if object has 3D model"""
        if obj.model_3d:
            return format_html('<span style="color: green;">✓ 3D Model</span>')
        return format_html('<span style="color: gray;">No 3D</span>')
    has_3d_model.short_description = '3D Model'
    
    def likes_count(self, obj):
        """Show number of likes"""
        return obj.likes.count()
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        """Show number of comments"""
        return obj.comments.filter(is_deleted=False).count()
    comments_count.short_description = 'Comments'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('likes', 'comments')

    fieldsets = (
        ("🏛️ Core Information", {
            "description": "Essential information about the heritage object",
            "fields": (
                "title", "title_ar", "title_fr",
                "description", "description_ar", "description_fr", 
                "region",
                "object_type",
                "ich_domain",
                ("origin_date", "date_text"),
            )
        }),
        ("📸 Media", {
            "description": "Images and 3D models for visualization",
            "fields": (
                "image",
                "model_3d",
            )
        }),
        ("📝 Identification Details", {
            "classes": ("collapse",),
            "description": "Additional identification information",
            "fields": ("alternate_name", "maker", "attribution", "copy_after", "sitter",
                       "period", "origin_place"),
        }),
        ("🏺 Provenance & Collection", {
            "classes": ("collapse",),
            "description": "History and collection information",
            "fields": ("provenance", "collector", "site_name", "field_identifier",
                      "collection_name", "on_view_location", "exhibition_history"),
        }),
        ("📏 Physical Properties", {
            "classes": ("collapse",),
            "description": "Materials and measurements",
            "fields": ("materials", "dimensions", "weight", "taxon"),
        }),
        ("⚖️ Rights & Metadata", {
            "classes": ("collapse",),
            "description": "Legal and technical information",
            "fields": ("credit_line", "data_source", "rights",
                       "accession_number", "object_number", "record_id", "metadata_usage",
                       "guid", "related_resource"),
        }),
    )

    class Media:
        css = {"all": ("admin/custom-admin.css", "admin/admin-override.css",)}


@admin.register(Submission, site=admin_site)
class SubmissionAdmin(admin.ModelAdmin):
    """Community submissions awaiting review"""
    list_display = ("title", "user", "status", "region", "object_type", "created_at")
    list_filter = ("status", "created_at", "region", "object_type", "ich_domain")
    search_fields = ("title", "description", "user__username", "user__email")
    raw_id_fields = ("user",)
    date_hierarchy = "created_at"
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    fieldsets = (
        ("📥 Submission Info", {
            "fields": ("user", "status")
        }),
        ("🏛️ Heritage Details", {
            "fields": ("title", "description", "region", "object_type", "ich_domain",
                      "origin_date", "date_text")
        }),
        ("📸 Media", {
            "fields": ("image", "model_3d")
        }),
        ("📝 Additional Information", {
            "classes": ("collapse",),
            "fields": ("alternate_name", "maker", "attribution", "copy_after", "sitter",
                      "period", "origin_place", "provenance", "collector", "site_name",
                      "field_identifier", "materials", "dimensions", "weight", "taxon")
        }),
        ("📅 Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    actions = ['approve_submissions', 'reject_submissions']
    
    def approve_submissions(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} submissions approved.')
    approve_submissions.short_description = "Approve selected submissions"
    
    def reject_submissions(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} submissions rejected.')
    reject_submissions.short_description = "Reject selected submissions"


@admin.register(EditProposal, site=admin_site)
class EditProposalAdmin(admin.ModelAdmin):
    """Proposed edits from community members"""
    list_display = ("user", "object", "status", "proposal_summary", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "object__title", "note")
    raw_id_fields = ("user", "object")
    date_hierarchy = "created_at"
    
    def proposal_summary(self, obj):
        """Show a summary of proposed changes"""
        if obj.data:
            changes = len(obj.data.keys()) if isinstance(obj.data, dict) else 0
            return f"{changes} field(s) changed"
        return "No changes"
    proposal_summary.short_description = "Changes"
    
    readonly_fields = ('created_at', 'updated_at', 'proposal_summary_detail')
    
    fieldsets = (
        ("✏️ Edit Proposal", {
            "fields": ("user", "object", "status")
        }),
        ("📝 Proposed Changes", {
            "fields": ("data", "note", "proposal_summary_detail")
        }),
        ("📅 Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def proposal_summary_detail(self, obj):
        """Show detailed summary of proposed changes in the form"""
        if obj and obj.data and isinstance(obj.data, dict):
            html = "<div style='background: #f8f9fa; padding: 10px; border-radius: 4px;'>"
            for field, value in obj.data.items():
                html += f"<strong>{field}:</strong> {value}<br>"
            html += "</div>"
            return format_html(html)
        return "No changes yet"
    proposal_summary_detail.short_description = "Proposed Changes Detail"
    
    actions = ['approve_edits', 'reject_edits']
    
    def approve_edits(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} edit proposals approved.')
    approve_edits.short_description = "Approve selected edits"
    
    def reject_edits(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} edit proposals rejected.')
    reject_edits.short_description = "Reject selected edits"


@admin.register(Comment, site=admin_site)
class CommentAdmin(admin.ModelAdmin):
    """User comments and discussions"""
    list_display = ("user", "object", "short_body", "is_deleted", "likes_count", "created_at")
    list_filter = ("is_deleted", "created_at")
    search_fields = ("body", "user__username", "user__email", "object__title")
    raw_id_fields = ("user", "object", "parent")
    date_hierarchy = "created_at"

    def short_body(self, obj):
        return (obj.body[:60] + "…") if len(obj.body) > 60 else obj.body
    short_body.short_description = "Comment"
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Likes"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('likes').select_related('user', 'object')
    
    actions = ['mark_deleted', 'mark_active']
    
    def mark_deleted(self, request, queryset):
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f'{updated} comments marked as deleted.')
    mark_deleted.short_description = "Mark as deleted"
    
    def mark_active(self, request, queryset):
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f'{updated} comments marked as active.')
    mark_active.short_description = "Mark as active"


@admin.register(HeritageLike, site=admin_site)
class HeritageLikeAdmin(admin.ModelAdmin):
    """Heritage object likes and favorites"""
    list_display = ("user", "object", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "object__title")
    raw_id_fields = ("user", "object")
    date_hierarchy = "created_at"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'object')


@admin.register(CommentLike, site=admin_site)
class CommentLikeAdmin(admin.ModelAdmin):
    """Comment likes"""
    list_display = ("user", "comment_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "comment__body")
    raw_id_fields = ("user", "comment")
    date_hierarchy = "created_at"
    
    def comment_preview(self, obj):
        body = obj.comment.body
        return (body[:50] + "…") if len(body) > 50 else body
    comment_preview.short_description = "Comment"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'comment')


@admin.register(UserProfile, site=admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    """Extended user profiles"""
    list_display = ("user", "rank", "heritage_contributions", "auth_method", "created_at")
    search_fields = ("user__username", "user__email", "bio")
    raw_id_fields = ("user",)
    list_filter = ("rank", "created_at")
    readonly_fields = ('created_at',)
    
    def heritage_contributions(self, obj):
        """Show number of submissions and edit proposals"""
        submissions = Submission.objects.filter(user=obj.user).count()
        edits = EditProposal.objects.filter(user=obj.user).count()
        return f"{submissions} submissions, {edits} edits"
    heritage_contributions.short_description = "Contributions"
    
    def auth_method(self, obj):
        """Show authentication method"""
        if hasattr(obj.user, 'socialaccount_set') and obj.user.socialaccount_set.exists():
            return format_html('<span style="color: #4285f4;">OAuth</span>')
        return format_html('<span style="color: #2C3E50;">Regular</span>')
    auth_method.short_description = "Auth"
    
    fieldsets = (
        ("👤 User Information", {
            "fields": ("user", "rank")
        }),
        ("📝 Profile Details", {
            "fields": ("bio", "location", "website", "twitter", "linkedin", "profile_photo_url")
        }),
        ("📅 Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )


# Register enhanced User admin with custom site
admin_site.register(User, EnhancedUserAdmin)

# Register allauth models with custom admin site
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib.sites.models import Site

# Email addresses (already registered by allauth, but we'll customize)
class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'primary', 'verified')
    list_filter = ('primary', 'verified')
    search_fields = ('email', 'user__username')
    raw_id_fields = ('user',)

# Social accounts 
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'uid', 'date_joined')
    list_filter = ('provider',)
    search_fields = ('user__username', 'user__email', 'uid')
    raw_id_fields = ('user',)

# Social applications (OAuth configs)
class SocialAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'client_id')
    list_filter = ('provider',)

# Social tokens
class SocialTokenAdmin(admin.ModelAdmin):
    list_display = ('account', 'app', 'expires_at')
    raw_id_fields = ('account', 'app')

# Sites
class SiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name')
    search_fields = ('domain', 'name')

# Register with custom admin site
try:
    admin_site.unregister(EmailAddress)
except:
    pass
try:
    admin_site.unregister(SocialAccount)
except:
    pass
try:
    admin_site.unregister(SocialApp)
except:
    pass
try:
    admin_site.unregister(SocialToken)
except:
    pass
try:
    admin_site.unregister(Site)
except:
    pass

admin_site.register(EmailAddress, EmailAddressAdmin)
admin_site.register(SocialAccount, SocialAccountAdmin)
admin_site.register(SocialApp, SocialAppAdmin)
admin_site.register(SocialToken, SocialTokenAdmin)
admin_site.register(Site, SiteAdmin)

# Also register with default admin for backwards compatibility
# Note: Using the same admin classes for both sites
@admin.register(HeritageObject)
class DefaultHeritageObjectAdmin(HeritageObjectAdmin):
    pass

@admin.register(Submission)
class DefaultSubmissionAdmin(SubmissionAdmin):
    pass

@admin.register(EditProposal)
class DefaultEditProposalAdmin(EditProposalAdmin):
    pass

@admin.register(Comment)
class DefaultCommentAdmin(CommentAdmin):
    pass

@admin.register(HeritageLike)
class DefaultHeritageLikeAdmin(HeritageLikeAdmin):
    pass

@admin.register(CommentLike)
class DefaultCommentLikeAdmin(CommentLikeAdmin):
    pass

@admin.register(UserProfile)
class DefaultUserProfileAdmin(UserProfileAdmin):
    pass

# Register User with default admin
admin.site.register(User, EnhancedUserAdmin)