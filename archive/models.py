from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class HeritageObject(models.Model):
    # ---------- Core choices (translatable labels) ----------
    REGION_CHOICES = [
        ('riyadh',   _('Riyadh')),
        ('makkah',   _('Makkah')),
        ('madinah',  _('Madinah')),
        ('qassim',   _('Qassim')),
        ('eastern',  _('Eastern Province')),
        ('asir',     _('Asir')),
        ('tabuk',    _('Tabuk')),
        ('hail',     _('Hail')),
        ('northern', _('Northern Borders')),
        ('jazan',    _('Jazan')),
        ('najran',   _('Najran')),
        ('bahah',    _('Al Bahah')),
        ('jouf',     _('Al Jouf')),
    ]

    # Includes all types you show in the UI
    TYPE_CHOICES = [
        ('tool',                 _('Tool')),
        ('vessel',               _('Vessel')),
        ('textile',              _('Textile')),
        ('jewellery',            _('Jewellery')),
        ('furniture',            _('Furniture')),
        ('ceramic',              _('Ceramic')),
        ('musical instrument',   _('Musical Instrument')),
        ('architecture',         _('Architecture')),
        ('manuscript',           _('Manuscript')),
        ('other',                _('Other')),
        ('architecture_element', _('Architecture Element')),  # kept for legacy/admin use
    ]

    ICH_CHOICES = [
        ('oral',      _('Oral Traditions')),
        ('arts',      _('Performing Arts')),
        ('rituals',   _('Social Practices & Rituals')),
        ('knowledge', _('Knowledge about Nature')),
        ('crafts',    _('Traditional Craftsmanship')),
    ]

    # ---------- Core fields ----------
    title = models.CharField(max_length=200, verbose_name=_("Title (English)"))
    title_ar = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Title (Arabic)"))
    title_fr = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Title (French)"))
    description = models.TextField(verbose_name=_("Description (English)"))
    description_ar = models.TextField(blank=True, null=True, verbose_name=_("Description (Arabic)"))
    description_fr = models.TextField(blank=True, null=True, verbose_name=_("Description (French)"))
    region = models.CharField(max_length=50, choices=REGION_CHOICES, default='riyadh')
    object_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='tool')
    ich_domain = models.CharField(
        max_length=50, choices=ICH_CHOICES, default='oral', verbose_name=_("ICH Domain")
    )
    origin_date = models.DateField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True, verbose_name=_("Thumbnail Image"))
    model_3d = models.FileField(upload_to='models/', null=True, blank=True, verbose_name=_("Model 3D"))

    # ---------- Optional Smithsonian-style metadata ----------
    alternate_name   = models.CharField(max_length=255, blank=True, null=True)
    maker            = models.CharField(_("Maker / Artist"), max_length=255, blank=True, null=True)
    attribution      = models.CharField(max_length=255, blank=True, null=True)
    copy_after       = models.CharField(max_length=255, blank=True, null=True)
    sitter           = models.CharField(max_length=255, blank=True, null=True)

    date_text     = models.CharField(max_length=255, blank=True, null=True)
    period        = models.CharField(max_length=255, blank=True, null=True)
    origin_place  = models.CharField(max_length=255, blank=True, null=True)

    provenance       = models.TextField(blank=True, null=True)
    collector        = models.CharField(max_length=255, blank=True, null=True)
    site_name        = models.CharField(max_length=255, blank=True, null=True)
    field_identifier = models.CharField(max_length=255, blank=True, null=True)

    materials   = models.TextField(blank=True, null=True)
    dimensions  = models.CharField(max_length=255, blank=True, null=True)
    weight      = models.CharField(max_length=255, blank=True, null=True)
    taxon       = models.CharField(_("Taxonomy"), max_length=255, blank=True, null=True)

    collection_name    = models.CharField(_("See more items in"), max_length=255, blank=True, null=True)
    on_view_location   = models.CharField(_("On View / Location"), max_length=255, blank=True, null=True)
    exhibition_history = models.TextField(blank=True, null=True)

    credit_line  = models.CharField(max_length=255, blank=True, null=True)
    data_source  = models.CharField(max_length=255, blank=True, null=True)
    rights       = models.CharField(_("Restrictions & Rights"), max_length=255, blank=True, null=True)

    accession_number = models.CharField(max_length=255, blank=True, null=True)
    object_number    = models.CharField(max_length=255, blank=True, null=True)
    record_id        = models.CharField(max_length=255, blank=True, null=True)
    metadata_usage   = models.CharField(max_length=255, blank=True, null=True)

    guid             = models.URLField(blank=True, null=True)
    related_resource = models.URLField(blank=True, null=True)

    def get_title_display(self, language_code=None):
        """Return appropriate title based on language"""
        from django.utils import translation
        
        if language_code is None:
            language_code = translation.get_language()
            
        if language_code == 'ar' and self.title_ar:
            return self.title_ar
        elif language_code == 'fr' and self.title_fr:
            return self.title_fr
        return self.title
    
    def get_description_display(self, language_code=None):
        """Return appropriate description based on language"""
        from django.utils import translation
        
        if language_code is None:
            language_code = translation.get_language()
            
        if language_code == 'ar' and self.description_ar:
            return self.description_ar
        elif language_code == 'fr' and self.description_fr:
            return self.description_fr
        return self.description
    
    def __str__(self):
        return self.title


# ============================
# Community / social models
# ============================

class HeritageLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    object = models.ForeignKey(HeritageObject, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "object"),)
        indexes = [
            models.Index(fields=["user", "object"]),
        ]

    def __str__(self):
        return f"{self.user} ♥ {self.object}"


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    object = models.ForeignKey(HeritageObject, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user} on {self.object}"
    
    @property
    def like_count(self):
        return self.likes.count()
    
    @property
    def reply_count(self):
        return self.replies.filter(is_deleted=False).count()


class CommentLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("user", "comment"),)
        indexes = [
            models.Index(fields=["user", "comment"]),
        ]

    def __str__(self):
        return f"{self.user} 👍 {self.comment_id}"


class EditProposal(models.Model):
    STATUS_CHOICES = [
        ("pending",  _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    object = models.ForeignKey(HeritageObject, on_delete=models.CASCADE, related_name="proposals")
    note = models.TextField(blank=True, null=True)
    data = models.JSONField()  # JSON of proposed changes
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Proposal by {self.user} on {self.object} ({self.status})"


class Submission(models.Model):
    STATUS_CHOICES = [
        ("pending",  _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Core trilingual fields
    title = models.CharField(max_length=200, verbose_name=_("Title (English)"))
    title_ar = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Title (Arabic)"))
    title_fr = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Title (French)"))
    description = models.TextField(verbose_name=_("Description (English)"))
    description_ar = models.TextField(blank=True, null=True, verbose_name=_("Description (Arabic)"))
    description_fr = models.TextField(blank=True, null=True, verbose_name=_("Description (French)"))
    
    region = models.CharField(max_length=50, choices=HeritageObject.REGION_CHOICES)
    object_type = models.CharField(max_length=50, choices=HeritageObject.TYPE_CHOICES)
    ich_domain = models.CharField(max_length=50, choices=HeritageObject.ICH_CHOICES)
    origin_date = models.DateField()
    image = models.ImageField(upload_to='submissions/images/', null=True, blank=True)
    model_3d = models.FileField(upload_to='submissions/models/', null=True, blank=True)

    # Optional metadata fields (same as HeritageObject)
    alternate_name = models.CharField(max_length=255, blank=True, null=True)
    maker = models.CharField(_("Maker / Artist"), max_length=255, blank=True, null=True)
    attribution = models.CharField(max_length=255, blank=True, null=True)
    period = models.CharField(max_length=255, blank=True, null=True)
    origin_place = models.CharField(max_length=255, blank=True, null=True)
    materials = models.TextField(blank=True, null=True)
    dimensions = models.CharField(max_length=255, blank=True, null=True)
    weight = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Submission: {self.title} ({self.status})"
    
    def should_auto_approve(self):
        """Check if this submission should be auto-approved based on user privileges"""
        # Auto-approve for staff, superusers, or high-ranking users
        profile = getattr(self.user, 'userprofile', None)
        if not profile:
            return False
            
        # Auto-approve for admins, experts, consultants, moderators
        return (
            self.user.is_staff or 
            self.user.is_superuser or 
            profile.rank >= 997  # Expert (999), Consultant (998), Moderator (997)
        )
    
    def create_heritage_object(self):
        """Convert approved submission to HeritageObject"""
        if self.status != 'approved':
            raise ValueError("Can only create HeritageObject from approved submissions")
            
        heritage_obj = HeritageObject.objects.create(
            title=self.title,
            title_ar=self.title_ar,
            title_fr=self.title_fr,
            description=self.description,
            description_ar=self.description_ar,
            description_fr=self.description_fr,
            region=self.region,
            object_type=self.object_type,
            ich_domain=self.ich_domain,
            origin_date=self.origin_date,
            image=self.image,
            model_3d=self.model_3d,
            alternate_name=self.alternate_name,
            maker=self.maker,
            attribution=self.attribution,
            period=self.period,
            origin_place=self.origin_place,
            materials=self.materials,
            dimensions=self.dimensions,
            weight=self.weight,
        )
        return heritage_obj


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_photo_url = models.URLField(blank=True, null=True)  # Google profile photo URL
    rank = models.PositiveIntegerField(default=1)  # simple gamification hook
    created_at = models.DateTimeField(auto_now_add=True)

    def get_activity_count(self):
        """Get total activity count (submitted objects + comments)"""
        
        # Count submissions by this user (from Submission model)
        submitted_objects = Submission.objects.filter(user=self.user).count()
        
        # Count comments by this user
        comments = Comment.objects.filter(user=self.user).count()
        
        return submitted_objects + comments
    
    def get_activity_rank(self):
        """Get activity-based rank"""
        activity_count = self.get_activity_count()
        
        if activity_count >= 100:
            return _("Advanced Digitizer")
        elif activity_count >= 50:
            return _("Intermediate Digitizer")
        elif activity_count >= 10:
            return _("Beginner Digitizer")
        else:
            return None
    
    def get_all_badges(self):
        """Get all applicable badges for this user"""
        badges = []
        
        # Administrative badges (highest priority)
        if self.user.is_superuser:
            badges.append({
                'text': _("Site Creator"),
                'class': 'bg-purple-100 text-purple-800 border-purple-300'
            })
        elif self.user.is_staff:
            badges.append({
                'text': _("Admin"),
                'class': 'bg-red-100 text-red-800 border-red-300'
            })
        
        # Manual special ranks (stored in profile)
        if self.rank == 999:  # Special code for Expert
            badges.append({
                'text': _("Expert"),
                'class': 'bg-indigo-100 text-indigo-800 border-indigo-300'
            })
        elif self.rank == 998:  # Special code for Consultant
            badges.append({
                'text': _("Consultant"),
                'class': 'bg-cyan-100 text-cyan-800 border-cyan-300'
            })
        elif self.rank == 997:  # Special code for Moderator
            badges.append({
                'text': _("Moderator"),
                'class': 'bg-orange-100 text-orange-800 border-orange-300'
            })
        
        # Activity-based badges
        activity_rank = self.get_activity_rank()
        if activity_rank:
            badges.append({
                'text': activity_rank,
                'class': 'bg-green-100 text-green-800 border-green-300'
            })
        
        return badges
    
    def get_rank_display(self):
        """Return the primary rank display for backward compatibility"""
        badges = self.get_all_badges()
        if badges:
            return badges[0]['text']
        else:
            return str(self.rank)
    
    def __str__(self):
        return f"Profile: {self.user}"