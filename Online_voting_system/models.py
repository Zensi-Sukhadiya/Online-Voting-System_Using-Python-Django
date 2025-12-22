from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.

User = get_user_model()

# StudentDetail Part
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    roll_no = models.CharField(max_length=50, blank=True)
    department = models.ForeignKey("Category", on_delete=models.CASCADE)  
    year = models.IntegerField(blank=True, null=True)  
    division = models.CharField(max_length=10, blank=True, null=True)  

    def save(self, *args, **kwargs):
        if not self.roll_no:
            # Stream-wise roll number count
            existing = StudentProfile.objects.filter(department=self.department).count() + 1
            self.roll_no = str(existing)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.department.name} - Year {self.year})"

    class Meta:
        ordering = ["department", "roll_no"]   
        unique_together = ("department", "roll_no")  
        

# Contact Part
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    student_id = models.CharField(max_length=50, blank=True, null=True)
    field = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"
    

# Category Part
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  

    def __str__(self):
        return self.name
    

# Committee Part
class Committee(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="committees")
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=False)   
    show_live_results = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    

# Candidate Part
class Candidate(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name="candidates", blank=True, null=True)
    name = models.CharField(max_length=150)
    department = models.CharField(max_length=100, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    roll_no = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='candidates/', blank=True, null=True)  
    is_active = models.BooleanField(default=False)  
    
    def __str__(self):
        return self.name 
    
    
# Vote Part
class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="votes")
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "committee"], name="unique_user_committee_vote")
        ]

    def __str__(self):
        return f"{self.user} → {self.candidate} ({self.committee})"


# Result Part
class Result(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="results")
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)
    total_votes = models.PositiveIntegerField(default=0)
    declared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate} - {self.total_votes} votes"