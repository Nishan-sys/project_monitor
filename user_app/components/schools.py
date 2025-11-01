from django_unicorn.components import UnicornView
from user_app.models import Division, School

class SchoolsView(UnicornView):
    division_id = None
    selected_division_id = ""
    selected_school_id = ""
    
    divisions = []
    schools = []
    
    def mount(self):
        """Component load වෙද්දී"""
        # URL එකෙන් division_id එක තියෙනවා නම්
        if self.division_id:
            self.selected_division_id = str(self.division_id)
        
        # සියලු divisions load කරනවා
        self.divisions = Division.objects.all().order_by('name')
        
        # Division එකක් pre-selected නම් schools load කරනවා
        if self.selected_division_id:
            self.load_schools()
    
    def updated_selected_division_id(self, value):
        """Division dropdown වෙනස් වෙද්දී"""
        self.selected_school_id = ""
        self.load_schools()
    
    def load_schools(self):
        """Schools load කරන්න"""
        if self.selected_division_id:
            self.schools = School.objects.filter(division_id=self.selected_division_id).select_related('division').order_by('census_number')
        else:
            self.schools = []
    
    def get_selected_division(self):
        """තෝරාගත් division එක"""
        if self.selected_division_id:
            try:
                return Division.objects.get(id=self.selected_division_id)
            except Division.DoesNotExist:
                return None
        return None
    
    def get_selected_school(self):
        """තෝරාගත් school එක"""
        if self.selected_school_id:
            try:
                return School.objects.get(id=self.selected_school_id)
            except School.DoesNotExist:
                return None
        return None
    
    def reset(self):
        """Reset කරන්න"""
        self.selected_division_id = ""
        self.selected_school_id = ""
        self.schools = []