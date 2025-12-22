from django.contrib import admin
from .models import StudentProfile
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth import logout
from .models import Contact, Category, Committee, Candidate, Vote, Result


# Register your models here.

# StudentDetail Model
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "roll_no", "department", "year", "division")
    search_fields = ("user__username", "roll_no")
    list_filter = ("department", "year", "division")


# Contact Model
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "student_id", "field", "subject", "created_at")
    search_fields = ("name", "email", "subject")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


# Committee
class CommitteeInline(admin.TabularInline):
    model = Committee
    extra = 2   
    min_num = 1 


# Candidate
class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1


# Category Model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "has_active_voting")
    inlines = [CommitteeInline]
    search_fields = ("name",)
    list_filter = ("name",)

    def has_active_voting(self, obj):
        active_committees = obj.committees.filter(is_active=True).exists()
        color = "green" if active_committees else "red"
        status = "Active" if active_committees else "Inactive"
        return format_html('<b><span style="color: {};">{}</span></b>', color, status)
    has_active_voting.short_description = "Voting Status"


# Committee Model
@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active_status")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    inlines = [CandidateInline]  
    actions = ["start_voting", "stop_voting"]

    # Activre Committee
    def is_active_status(self, obj):
        color = "green" if obj.is_active else "red"
        status = "Active" if obj.is_active else "Inactive"
        return format_html('<b><span style="color: {};">{}</span></b>', color, status)
    is_active_status.short_description = "Voting Status"

    # Start Voting
    def start_voting(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Start Voting for selected committees")

        #  Admin auto logout after activation
        logout(request)

        #  Redirect to login page after logout
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect("/login/")

    # Stop Voting
    def stop_voting(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Stop Voting for selected committees")

    start_voting.short_description = "Start Voting"
    stop_voting.short_description = "Stop Voting"

    # Buttons
    def activate_button(self, obj):
        if not obj.is_active:
            url = reverse("activate_committee", args=[obj.id])
            return format_html('<a class="button" href="{}">Activate</a>', url)
        return "Active"
    
    activate_button.short_description = "Activate Voting"
    activate_button.allow_tags = True


# Candidate Model
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "year", "roll_no", "committee", "is_active")
    list_filter = ("committee__category", "committee")
    search_fields = ("name", "roll_no",)


# Vote Model
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("user", "candidate", "committee", "created_at")
    list_filter = ("committee", "created_at")
    search_fields = ("name",)


# Result Model
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("candidate", "committee", "total_votes", "declared_at")
    list_filter = ("committee", "declared_at")
    search_fields = ("candidate__name",)