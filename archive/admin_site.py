from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.template.response import TemplateResponse


class TurathAdminSite(AdminSite):
    site_header = 'Turath3D Administration'
    site_title = 'Turath3D Admin'
    index_title = 'Heritage Management Dashboard'
    
    def get_app_list(self, request, app_label=None):
        """
        Reorganize the admin index to prioritize Heritage Objects and group related models
        """
        app_list = super().get_app_list(request, app_label)
        
        # Custom ordering and grouping
        heritage_models = []
        user_models = []
        community_models = []
        system_models = []
        
        for app in app_list:
            if app['app_label'] == 'archive':
                for model in app['models']:
                    model_name = model['object_name']
                    
                    # Add descriptions to each model
                    if model_name == 'HeritageObject':
                        model['description'] = 'Core heritage items: artifacts, sites, and cultural objects with 3D models'
                        model['priority'] = True
                        heritage_models.append(model)
                    elif model_name == 'Submission':
                        model['description'] = 'Community-submitted heritage items awaiting review and approval'
                        heritage_models.append(model)
                    elif model_name == 'EditProposal':
                        model['description'] = 'Proposed edits to existing heritage objects from community members'
                        heritage_models.append(model)
                    elif model_name == 'Comment':
                        model['description'] = 'User comments and discussions on heritage objects'
                        community_models.append(model)
                    elif model_name == 'HeritageLike':
                        model['description'] = 'User likes and favorites for heritage objects'
                        community_models.append(model)
                    elif model_name == 'CommentLike':
                        model['description'] = 'User likes for comments'
                        community_models.append(model)
                    elif model_name == 'UserProfile':
                        model['description'] = 'Extended user profiles with ranks and achievements'
                        user_models.append(model)
                        
            elif app['app_label'] == 'auth':
                for model in app['models']:
                    if model['object_name'] == 'User':
                        model['description'] = 'System users (both registered and OAuth authenticated)'
                        user_models.append(model)
                    elif model['object_name'] == 'Group':
                        model['description'] = 'User groups for permission management'
                        user_models.append(model)
                        
            elif app['app_label'] == 'socialaccount':
                for model in app['models']:
                    model_name = model['object_name']
                    if model_name == 'SocialAccount':
                        model['description'] = 'Google and other OAuth provider accounts'
                        user_models.append(model)
                    elif model_name == 'SocialApplication':
                        model['description'] = 'OAuth application configurations (Google, etc.)'
                        system_models.append(model)
                    elif model_name == 'SocialToken':
                        model['description'] = 'OAuth tokens for authenticated users'
                        system_models.append(model)
                        
            elif app['app_label'] == 'account':
                for model in app['models']:
                    if model['object_name'] == 'EmailAddress':
                        model['description'] = 'User email addresses and verification status'
                        user_models.append(model)
                        
            elif app['app_label'] == 'sites':
                for model in app['models']:
                    model['description'] = 'Django sites framework - used for domain management'
                    system_models.append(model)
        
        # Create reorganized app list
        new_app_list = []
        
        # Heritage Content (Priority)
        if heritage_models:
            new_app_list.append({
                'name': '🏛️ Heritage Content Management',
                'app_label': 'heritage_content',
                'app_url': '/admin/archive/',
                'has_module_perms': True,
                'models': heritage_models,
                'description': 'This is the core of your website. Here you manage all heritage objects (artifacts, cultural sites, traditional items) with their 3D models, images, and detailed metadata. You can also review and approve community submissions, and handle edit proposals from users who want to improve existing content.'
            })
        
        # User Management
        if user_models:
            new_app_list.append({
                'name': '👥 User & Authentication',
                'app_label': 'user_management',
                'app_url': '/admin/auth/',
                'has_module_perms': True,
                'models': user_models,
                'description': 'Manage all users of your platform. This includes both users who registered directly and those who signed in via Google OAuth. You can view user profiles, manage permissions through groups, verify email addresses, and track which authentication method each user is using.'
            })
        
        # Community Engagement
        if community_models:
            new_app_list.append({
                'name': '💬 Community Engagement',
                'app_label': 'community',
                'app_url': '/admin/archive/',
                'has_module_perms': True,
                'models': community_models,
                'description': 'Monitor and moderate community interactions. Review user comments on heritage objects, manage likes and favorites, and handle any inappropriate content. This helps maintain a positive and educational environment for all users interested in cultural heritage.'
            })
        
        # System Configuration
        if system_models:
            new_app_list.append({
                'name': '⚙️ System Configuration',
                'app_label': 'system',
                'app_url': '/admin/',
                'has_module_perms': True,
                'models': system_models,
                'description': 'Technical configuration for the website. OAuth Applications manages Google Sign-In integration (Client ID and Secret). Sites framework defines your domain (required by django-allauth for OAuth redirects). Social Tokens stores OAuth authentication tokens for users who sign in with Google.'
            })
        
        return new_app_list
    
    def index(self, request, extra_context=None):
        """
        Display the main admin index page with custom styling and organization
        """
        extra_context = extra_context or {}
        extra_context['custom_welcome'] = True
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = TurathAdminSite(name='turath_admin')