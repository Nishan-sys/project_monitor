from django_unicorn.components import UnicornView
from user_app.models import Division, School


class SchoolsListView(UnicornView):
    selected_division_id: int = None
    divisions = []
    schools = []

    def mount(self):
        """Runs when component loads"""
        self.divisions = Division.objects.all()

    def updated_selected_division_id(self):
        """Runs automatically when division changes"""
        print("Selected Division ID:", self.selected_division_id)
        if self.selected_division_id:
            self.schools = School.objects.filter(division_id=self.selected_division_id)
            print("Schools found:", self.schools.count())
        else:
            self.schools = []
