from __future__ import annotations

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext

from .models import (
    HeritageObject,
    HeritageLike,
    Comment,
    CommentLike,
    EditProposal,
    Submission,
    UserProfile,
)

# ---------- FORMS ----------

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a public comment…"}),
        }


class ProposeEditForm(forms.Form):
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Explain your suggestion (optional)"}),
        label="Note",
    )
    data = forms.JSONField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 8, "placeholder": '{"title": "...", "description": "..."}'}),
        label="Proposed changes (JSON)",
    )


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = [
            "title", "title_ar", "title_fr",
            "description", "description_ar", "description_fr", 
            "region", "object_type", "ich_domain", "origin_date",
            "image", "model_3d",
            # Optional metadata
            "alternate_name", "maker", "attribution", "period", "origin_place",
            "materials", "dimensions", "weight",
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'placeholder': _('Enter title in English')
            }),
            'title_ar': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'placeholder': _('Enter title in Arabic (optional)'),
                'dir': 'rtl'
            }),
            'title_fr': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'placeholder': _('Enter title in French (optional)')
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'rows': 4,
                'placeholder': _('Describe the object in English')
            }),
            'description_ar': forms.Textarea(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'rows': 4,
                'placeholder': _('Describe the object in Arabic (optional)'),
                'dir': 'rtl'
            }),
            'description_fr': forms.Textarea(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'rows': 4,
                'placeholder': _('Describe the object in French (optional)')
            }),
            'origin_date': forms.DateInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'type': 'date'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'accept': 'image/*'
            }),
            'model_3d': forms.FileInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'accept': '.obj,.ply,.stl,.gltf,.glb'
            }),
            # Optional metadata fields
            'alternate_name': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold'
            }),
            'maker': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold'
            }),
            'attribution': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold'
            }),
            'period': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold'
            }),
            'origin_place': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold'
            }),
            'materials': forms.Textarea(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold',
                'rows': 2
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold'
            }),
            'weight': forms.TextInput(attrs={
                'class': 'w-full border border-brand-navy/20 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-gold/60 focus:border-brand-gold'
            }),
        }


# ---------- PUBLIC PAGES ----------

def _liked_ids_for(user):
    """Return a set of object IDs the user has liked (or empty set if anon)."""
    if not user.is_authenticated:
        return set()
    return set(
        HeritageLike.objects.filter(user=user).values_list("object_id", flat=True)
    )


def heritage_list(request):
    """List all objects."""
    objects = HeritageObject.objects.all().annotate(like_count=Count("likes"))
    liked_ids = _liked_ids_for(request.user)
    return render(
        request,
        "archive/heritage_list.html",
        {"objects": objects, "liked_ids": liked_ids, "filter_type": "all"},
    )


def heritage_filtered(request):
    """Filtering by region, type, and search query."""
    region = request.GET.get("region")
    obj_type = request.GET.get("type")
    q = request.GET.get("q")

    objects = HeritageObject.objects.all()

    if region:
        objects = objects.filter(region__iexact=region)

    if obj_type:
        objects = objects.filter(object_type__iexact=obj_type)

    if q and q.strip():
        objects = objects.filter(title__icontains=q)

    # add like counts for the badges
    objects = objects.annotate(like_count=Count("likes"))
    liked_ids = _liked_ids_for(request.user)

    return render(
        request,
        "archive/heritage_list.html",
        {
            "objects": objects,
            "filter_type": "combined",
            "region": region,
            "obj_type": obj_type,
            "q": q,
            "liked_ids": liked_ids,
        },
    )


def heritage_detail(request, pk: int):
    """Object detail + comments + like state."""
    obj = get_object_or_404(HeritageObject, pk=pk)

    # Get top-level comments sorted by likes (most liked first)
    comments = (
        Comment.objects.filter(object=obj, is_deleted=False, parent=None)
        .select_related("user__userprofile")
        .prefetch_related("likes", "replies__user__userprofile", "replies__likes")
        .annotate(likes_count=Count("likes"))
        .order_by("-likes_count", "-created_at")
    )
    
    # Get user stats for comments
    comment_user_stats = {}
    for comment in comments:
        if comment.user_id not in comment_user_stats:
            user_profile, _ = UserProfile.objects.get_or_create(user=comment.user)
            comment_user_stats[comment.user_id] = {
                "profile": user_profile,
                "total_comments": Comment.objects.filter(user=comment.user, is_deleted=False).count(),
                "total_likes_received": CommentLike.objects.filter(comment__user=comment.user).count(),
            }
        # Check if current user liked this comment
        comment.user_liked = False
        if request.user.is_authenticated:
            comment.user_liked = comment.likes.filter(user=request.user).exists()
        
        # Process replies
        for reply in comment.replies.filter(is_deleted=False):
            if reply.user_id not in comment_user_stats:
                reply_profile, _ = UserProfile.objects.get_or_create(user=reply.user)
                comment_user_stats[reply.user_id] = {
                    "profile": reply_profile,
                    "total_comments": Comment.objects.filter(user=reply.user, is_deleted=False).count(),
                    "total_likes_received": CommentLike.objects.filter(comment__user=reply.user).count(),
                }
            reply.user_liked = False
            if request.user.is_authenticated:
                reply.user_liked = reply.likes.filter(user=request.user).exists()
    
    comment_form = CommentForm()

    user_liked = False
    if request.user.is_authenticated:
        user_liked = HeritageLike.objects.filter(user=request.user, object=obj).exists()

    context = {
        "object": obj,
        "comments": comments,
        "comment_form": comment_form,
        "user_liked": user_liked,
        "comment_user_stats": comment_user_stats,
        # Add field choices for edit form
        "region_choices": HeritageObject.REGION_CHOICES,
        "type_choices": HeritageObject.TYPE_CHOICES,
        "ich_choices": HeritageObject.ICH_CHOICES,
    }
    return render(request, "archive/heritage_detail.html", context)


# ---------- STATIC PAGES ----------

def home(request):
    return render(request, "archive/home.html")


def about(request):
    return render(request, "archive/about.html")


def sponsors(request):
    return render(request, "archive/sponsors.html")


def donate(request):
    return render(request, "archive/donate.html")


# ---------- SOCIAL ACTIONS (likes & comments) ----------

@login_required
def toggle_like(request, pk: int):
    obj = get_object_or_404(HeritageObject, pk=pk)
    like, created = HeritageLike.objects.get_or_create(user=request.user, object=obj)
    if not created:
        like.delete()
        messages.success(request, "Removed like.")
    else:
        messages.success(request, "Liked.")
    return redirect("heritage-detail", pk=obj.pk)


@login_required
def post_comment(request, pk: int):
    if request.method != "POST":
        return HttpResponseForbidden("POST required")

    obj = get_object_or_404(HeritageObject, pk=pk)
    form = CommentForm(request.POST)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        if form.is_valid():
            comment = Comment.objects.create(
                user=request.user,
                object=obj,
                body=form.cleaned_data["body"],
            )
            
            # Get user stats for the new comment
            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
            comment_user_stats = {
                request.user.id: {
                    "profile": user_profile,
                    "total_comments": Comment.objects.filter(user=request.user, is_deleted=False).count(),
                    "total_likes_received": CommentLike.objects.filter(comment__user=request.user).count(),
                }
            }
            
            # Set like status
            comment.user_liked = False
            
            # Render comment HTML
            comment_html = render_to_string('archive/comment_partial.html', {
                'c': comment,
                'comment_user_stats': comment_user_stats,
                'request': request,
            })
            
            return JsonResponse({
                'success': True,
                'message': 'Comment posted successfully!',
                'comment_html': comment_html,
                'comment_id': comment.id
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Please fix the errors in your comment.',
                'errors': form.errors
            })
    
    # Regular form submission (fallback)
    if form.is_valid():
        Comment.objects.create(
            user=request.user,
            object=obj,
            body=form.cleaned_data["body"],
        )
        messages.success(request, "Comment posted.")
    else:
        messages.error(request, "Please fix the errors in your comment.")

    return redirect("heritage-detail", pk=obj.pk)


@login_required
def delete_comment(request, comment_id: int):
    comment = get_object_or_404(Comment, pk=comment_id)
    obj_pk = comment.object_id

    if not (request.user.is_staff or comment.user_id == request.user.id):
        return HttpResponseForbidden("Not allowed")

    if hasattr(comment, "is_deleted"):
        comment.is_deleted = True
        comment.save(update_fields=["is_deleted"])
    else:
        comment.delete()

    messages.success(request, "Comment removed.")
    return redirect("heritage-detail", pk=obj_pk)


@login_required
def toggle_comment_like(request, comment_id: int):
    comment = get_object_or_404(Comment, pk=comment_id, is_deleted=False)
    obj_pk = comment.object_id

    like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
    liked = True
    if not created:
        like.delete()
        liked = False
        messages.success(request, "Removed like.")
    else:
        messages.success(request, "Liked.")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        like_count = comment.likes.count()
        return JsonResponse({
            'success': True,
            'liked': liked,
            'like_count': like_count,
            'message': 'Liked!' if liked else 'Like removed!'
        })
    
    return redirect("heritage-detail", pk=obj_pk)


@login_required
def post_comment_reply(request, comment_id: int):
    if request.method != "POST":
        return HttpResponseForbidden("POST required")
    
    parent_comment = get_object_or_404(Comment, pk=comment_id, is_deleted=False)
    obj_pk = parent_comment.object_id
    
    body = request.POST.get("body", "").strip()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        if body:
            reply = Comment.objects.create(
                user=request.user,
                object=parent_comment.object,
                parent=parent_comment,
                body=body,
            )
            
            # Get user stats for the reply
            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
            comment_user_stats = {
                request.user.id: {
                    "profile": user_profile,
                    "total_comments": Comment.objects.filter(user=request.user, is_deleted=False).count(),
                    "total_likes_received": CommentLike.objects.filter(comment__user=request.user).count(),
                }
            }
            
            # Set like status
            reply.user_liked = False
            
            # Render reply HTML
            reply_html = render_to_string('archive/reply_partial.html', {
                'reply': reply,
                'comment_user_stats': comment_user_stats,
                'request': request,
            })
            
            return JsonResponse({
                'success': True,
                'message': 'Reply posted successfully!',
                'reply_html': reply_html,
                'parent_comment_id': parent_comment.id,
                'reply_count': parent_comment.replies.filter(is_deleted=False).count()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Reply cannot be empty.'
            })
    
    # Regular form submission (fallback)
    if body:
        Comment.objects.create(
            user=request.user,
            object=parent_comment.object,
            parent=parent_comment,
            body=body,
        )
        messages.success(request, "Reply posted.")
    else:
        messages.error(request, "Reply cannot be empty.")
    
    return redirect("heritage-detail", pk=obj_pk)


# ---------- COMMUNITY CONTRIBUTIONS ----------

@login_required
def propose_edit(request, pk: int):
    obj = get_object_or_404(HeritageObject, pk=pk)

    if request.method == "POST":
        form = ProposeEditForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data["data"]
            note = form.cleaned_data.get("note", "")

            EditProposal.objects.create(
                user=request.user,
                object=obj,
                data=data,
                note=note,
                status="pending",
            )
            messages.success(request, "Your edit proposal was submitted for review.")
            return redirect("heritage-detail", pk=obj.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProposeEditForm()

    return render(request, "archive/propose_edit.html", {"object": obj, "form": form})


@login_required
def propose_edit_inline(request, pk: int):
    """Handle inline edit submissions with permission-based auto-approval"""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST required"})
    
    obj = get_object_or_404(HeritageObject, pk=pk)
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({"success": False, "message": "AJAX request required"})
    
    try:
        # Collect all the edited fields
        edited_data = {}
        
        # Core fields
        core_fields = [
            'title', 'title_ar', 'title_fr',
            'description', 'description_ar', 'description_fr',
            'region', 'object_type', 'ich_domain', 'origin_date'
        ]
        
        # Optional metadata fields
        optional_fields = [
            'alternate_name', 'maker', 'attribution', 'period',
            'origin_place', 'materials', 'dimensions', 'weight'
        ]
        
        # Collect changed fields only
        for field in core_fields + optional_fields:
            if field in request.POST:
                new_value = request.POST.get(field, '').strip()
                # Get current value
                current_value = getattr(obj, field)
                if current_value is None:
                    current_value = ''
                # Convert date to string for comparison
                if field == 'origin_date' and current_value:
                    current_value = str(current_value)
                
                # Only include if changed
                if str(current_value) != new_value:
                    edited_data[field] = new_value
        
        if not edited_data:
            return JsonResponse({
                "success": False,
                "message": gettext("No changes detected")
            })
        
        # Check user permissions for auto-approval
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        auto_approve = (
            request.user.is_superuser or
            request.user.is_staff or
            user_profile.rank >= 997  # Expert (999), Consultant (998), Moderator (997)
        )
        
        if auto_approve:
            # Apply changes directly to the object
            for field, value in edited_data.items():
                if field == 'origin_date' and value:
                    # Parse date field
                    from datetime import datetime
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                elif value == '':
                    # Convert empty strings to None for optional fields
                    if field in optional_fields:
                        value = None
                
                setattr(obj, field, value)
            
            obj.save()
            
            # Create an approved EditProposal for record-keeping
            EditProposal.objects.create(
                user=request.user,
                object=obj,
                data=edited_data,
                note=f"Auto-approved edit by {user_profile.get_rank_display()}",
                status="approved"
            )
            
            return JsonResponse({
                "success": True,
                "message": gettext("Changes applied immediately!"),
                "auto_approved": True
            })
        else:
            # Create a pending EditProposal
            proposal = EditProposal.objects.create(
                user=request.user,
                object=obj,
                data=edited_data,
                note="Inline edit from heritage detail page",
                status="pending"
            )
            
            return JsonResponse({
                "success": True,
                "message": gettext("Your edit proposal has been submitted for review"),
                "auto_approved": False,
                "proposal_id": proposal.id
            })
    
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        })


@login_required
def submit_object(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission: Submission = form.save(commit=False)
            submission.user = request.user
            
            # Check if user has auto-approval privileges
            if submission.should_auto_approve():
                submission.status = "approved"
                submission.save()
                
                # Automatically create HeritageObject
                heritage_obj = submission.create_heritage_object()
                messages.success(request, f"✅ Your object '{heritage_obj.title}' has been published immediately! Your privileged status allows instant publication.")
                return redirect("heritage-detail", pk=heritage_obj.pk)
            else:
                submission.status = "pending"
                submission.save()
                messages.success(request, "📋 Thank you! Your submission is pending review by our moderation team.")
                
            return redirect("my-submissions")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SubmissionForm()

    # Check user's privilege level for the template
    user_profile = getattr(request.user, 'userprofile', None)
    has_auto_approval = (
        request.user.is_staff or 
        request.user.is_superuser or 
        (user_profile and user_profile.rank >= 997)
    )

    return render(request, "archive/submit_object.html", {
        "form": form,
        "has_auto_approval": has_auto_approval
    })


@login_required
def my_submissions(request):
    items = Submission.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "archive/my_submissions.html", {"items": items})


@login_required
def my_proposals(request):
    items = EditProposal.objects.filter(user=request.user).select_related("object").order_by("-created_at")
    return render(request, "archive/my_proposals.html", {"items": items})


# ---------- PROFILES ----------

@login_required
def me_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    likes_count = HeritageLike.objects.filter(user=request.user).count()
    comments_count = Comment.objects.filter(user=request.user, is_deleted=False).count()
    proposals_count = EditProposal.objects.filter(user=request.user).count()
    submissions_count = Submission.objects.filter(user=request.user).count()
    
    # Get recent submissions and proposals for the cards
    recent_submissions = Submission.objects.filter(user=request.user).order_by("-created_at")[:3]
    recent_proposals = EditProposal.objects.filter(user=request.user).select_related("object").order_by("-created_at")[:3]

    return render(
        request,
        "archive/me_dashboard.html",
        {
            "profile": profile,
            "stats": {
                "likes": likes_count,
                "comments": comments_count,
                "proposals": proposals_count,
                "submissions": submissions_count,
            },
            "recent_submissions": recent_submissions,
            "recent_proposals": recent_proposals,
        },
    )


def public_profile(request, username: str):
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=user)

    likes_count = HeritageLike.objects.filter(user=user).count()
    comments_count = Comment.objects.filter(user=user, is_deleted=False).count()
    
    # Get recent activity for the profile
    recent_likes = HeritageLike.objects.filter(user=user).select_related("object").order_by("-created_at")[:5]
    recent_comments = Comment.objects.filter(user=user, is_deleted=False).select_related("object").order_by("-created_at")[:3]

    return render(
        request,
        "archive/public_profile.html",
        {
            "profile_user": user, 
            "profile": profile, 
            "likes_count": likes_count, 
            "comments_count": comments_count,
            "recent_likes": recent_likes,
            "recent_comments": recent_comments,
        },
    )
