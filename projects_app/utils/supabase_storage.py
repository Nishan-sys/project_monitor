from supabase import create_client
from django.conf import settings
import uuid


supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def upload_pdf_to_supabase(file):
    file.seek(0)

    filename = f"{uuid.uuid4()}.pdf"

    supabase.storage.from_("project-reports").upload(
        filename,
        file.read(),
        {"content-type": "application/pdf"}
    )

    public_url = supabase.storage.from_("project-reports").get_public_url(filename)

    return public_url

