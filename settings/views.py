from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.management import call_command
from django.http import HttpResponse
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
import os, datetime
from django.conf import settings

# Helper: only allow Admins
def is_admin(user):
    return user.is_authenticated and getattr(user, "role", None) == "Admin"


# Role-based redirect after login

def role_redirect_view(request):
    user = request.user
    if hasattr(user, "role"):
        if user.role == "Admin":
            return redirect("settings:dashboard")
        elif user.role == "DataEntry":
            return redirect("data_collection:upload_excel")
        elif user.role == "Viewer":
            return redirect("visualization:dashboard")
        else:
            return redirect("reports:home")
    return redirect("home")


# Dashboard
@login_required
def dashboard(request):
    return render(request, "settings/dashboard.html")


# -------------------------
# USER MANAGEMENT
# -------------------------

@user_passes_test(is_admin)
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, "settings/user_list.html", {"users": users})



@user_passes_test(is_admin)
def add_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect("settings:user_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "settings/add_user.html", {"form": form})



@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Prevent editing other Admins unless editing self
    if user.role == "Admin" and user != request.user:
        messages.error(request, "You cannot edit another Admin’s account.")
        return redirect("settings:user_list")

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect("settings:user_list")
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, "settings/edit_user.html", {"form": form, "user": user})



@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Prevent Admin from deleting themselves
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("settings:user_list")

    # Prevent deleting the last Admin
    if user.role == "Admin" and CustomUser.objects.filter(role="Admin").count() == 1:
        messages.error(request, "You cannot delete the last Admin account.")
        return redirect("settings:user_list")

    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect("settings:user_list")


# -------------------------
# DATA BACKUP & RESTORE
# -------------------------

@user_passes_test(is_admin)
def backup_database(request):
    backup_dir = os.path.join(os.path.dirname(__file__), "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")

    with open(backup_file, "w") as f:
        call_command("dumpdata", stdout=f)

    with open(backup_file, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/json")
        response["Content-Disposition"] = f'attachment; filename="backup_{timestamp}.json"'
    return response



@user_passes_test(is_admin)
def restore_database(request):
    if request.method == "POST" and request.FILES.get("backup_file"):
        backup_file = request.FILES["backup_file"]

        # Validate extension
        filename = backup_file.name
        if not filename.endswith(".json"):
            messages.error(request, "Invalid file type. Please upload a JSON fixture file.")
            return redirect("settings:restore_database")

        temp_path = os.path.join(settings.BASE_DIR, "temp_backup.json")

        # Save uploaded file safely
        with open(temp_path, "wb+") as destination:
            for chunk in backup_file.chunks():
                destination.write(chunk)

        try:
            # Load data from fixture
            call_command("loaddata", temp_path)
            messages.success(request, "Database restored successfully.")
        except Exception as e:
            messages.error(request, f"Restore failed: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return redirect("settings:dashboard")

    return render(request, "settings/restore_database.html")


# -------------------------
# SYSTEM SETTINGS
# -------------------------

@user_passes_test(is_admin)
def system_settings(request):
    return render(request, "settings/system_settings.html")
