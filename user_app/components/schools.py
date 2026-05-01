# from django_unicorn.components import UnicornView
# from user_app.models import Division, School
# from django.contrib.auth.models import User

# class SchoolsView(UnicornView):
#     division_id = None
#     selected_division_id = ""
#     selected_school_id = ""

#     divisions = []
#     schools = []

#     def mount(self):
#         """Component loads — scope divisions by user's role"""
#         if self.division_id:
#             self.selected_division_id = str(self.division_id)

#         # Scope divisions based on the logged-in user's role
#         self.divisions = list(self._get_scoped_divisions())

#         if self.selected_division_id:
#             self.load_schools()

#     def _get_scoped_divisions(self):
#         """Return divisions the current user is allowed to see."""
#         user = self.request.user

#         print(f"USER: {user.username}")
#         print(f"IS AUTHENTICATED: {user.is_authenticated}")
#         print(f"HAS PROFILE: {hasattr(user, 'profile')}")

#         if not user.is_authenticated:
#             return Division.objects.none()

#         if hasattr(user, 'profile'):
#             print(f"ROLE: {user.profile.role}")
#             print(f"ZONE: {user.profile.zone}")
#             role = user.profile.role

#             if role == 'provincial':
#                 # Provincial sees all divisions
#                 return Division.objects.all().select_related('zone').order_by('name')

#             elif role == 'zonal':
#                 # Zonal sees only divisions in their zone
#                 zone = user.profile.zone
#                 if zone:
#                     return Division.objects.filter(
#                         zone=zone
#                     ).select_related('zone').order_by('name')
#                 return Division.objects.none()

#         # School users, divisional directors — no access
#         return Division.objects.none()

#     def updated_selected_division_id(self, value):
#         """Division dropdown changed"""
#         self.selected_school_id = ""
#         self.load_schools()

#     def load_schools(self):
#         """Load schools for selected division"""
#         if self.selected_division_id:
#             self.schools = list(
#                 School.objects.filter(
#                     division_id=self.selected_division_id
#                 ).select_related('division').order_by('census_number')
#             )
#         else:
#             self.schools = []

#     def get_selected_division(self):
#         if self.selected_division_id:
#             try:
#                 return Division.objects.get(id=self.selected_division_id)
#             except Division.DoesNotExist:
#                 return None
#         return None

#     def get_selected_school(self):
#         if self.selected_school_id:
#             try:
#                 return School.objects.get(id=self.selected_school_id)
#             except School.DoesNotExist:
#                 return None
#         return None

#     def reset(self):
#         self.selected_division_id = ""
#         self.selected_school_id = ""
#         self.schools = []


from django_unicorn.components import UnicornView
from user_app.models import Division, School

class SchoolsView(UnicornView):
    division_id = None
    selected_division_id = ""

    def _get_scoped_divisions(self):
        user = self.request.user
        if not user.is_authenticated:
            return Division.objects.none()
        if hasattr(user, 'profile'):
            role = user.profile.role
            if role == 'provincial':
                return Division.objects.all().order_by('name')
            elif role == 'zonal':
                zone = user.profile.zone
                if zone:
                    return Division.objects.filter(zone=zone).order_by('name')
        return Division.objects.none()

    def _get_schools(self):
        if self.selected_division_id:
            return School.objects.filter(
                division_id=self.selected_division_id
            ).order_by('census_number')
        return School.objects.none()

    def mount(self):
        if self.division_id:
            self.selected_division_id = str(self.division_id)

    def updated_selected_division_id(self, value):
        """Triggered automatically when dropdown changes"""
        self.selected_division_id = value

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = self._get_scoped_divisions()
        context['schools'] = self._get_schools()
        return context