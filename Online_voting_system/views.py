from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from .models import Contact, Category, Committee, Candidate, Vote, StudentProfile
from .forms import UserRegisterForm


# Create your views here.

@login_required(login_url='/login/')
def index(request):
    return render(request, "index.html")

@login_required
def services(request):
    return render(request, 'services.html')

@login_required
def about(request):
    return render(request, 'about-us.html')


@login_required
def results(request):
    committee_id = request.GET.get("committee") or request.session.get("current_committee_id")

    if not committee_id:
        messages.error(request, "No active committee selected for results.")
        return redirect("category")

    committee = get_object_or_404(Committee, id=committee_id)

    if committee.is_active and not committee.show_live_results:
        messages.info(request, "⚠️ Results will be available only after voting ends.")
        return redirect("category")

    candidates = Candidate.objects.filter(committee=committee)

    results = []
    for c in candidates:
        votes = Vote.objects.filter(candidate=c).count()
        results.append({"candidate": c, "votes": votes})

    # Find Winner 
    winner = None
    tie = False
    if results:
        max_votes = max(r["votes"] for r in results)
        winners = [r["candidate"] for r in results if r["votes"] == max_votes]

        if len(winners) == 1:
            winner = winners[0]
        else:
            tie = True  

    return render(request, "results.html", {
        "committee": committee,
        "results": results,
        "winner": winner,
        "tie": tie,
        "winners": winners if tie else [],
    })
    

@login_required
def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("tel")
        student_id = request.POST.get("number")
        field = request.POST.get("field")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            student_id=student_id,
            field=field,
            subject=subject,
            message=message,
        )

        messages.success(request, "✅ Your message has been sent successfully!")
        return redirect("contact-us")
    
    return render(request, 'contact-us.html')


@login_required
def category(request):
    categories = Category.objects.prefetch_related("committees").all()
    return render(request, "category.html", {"categories": categories})


@login_required
def voting(request):
    stream_id = request.GET.get("stream")
    committee_id = request.GET.get("committee")

    if not stream_id or not committee_id:
        return render(request, "voting.html", {
            "candidates": [],
            "stream_label": "Not Selected",
            "committee_label": "Not Selected"
        })
    
    category_obj = get_object_or_404(Category, pk=stream_id)
    committee_obj = get_object_or_404(Committee, pk=committee_id)

    candidates = Candidate.objects.filter(committee__category_id=stream_id, committee_id=committee_id)
    ctx = {
        "stream_key": category_obj.id,
        "committee_key": committee_obj.id,
        "stream_label": Category.objects.get(id=stream_id).name,
        "committee_label": Committee.objects.get(id=committee_id).name,
        "candidates": candidates,
    }
    return render(request, "voting.html", ctx)


@login_required
def vote(request):
    if request.method == "POST":
        candidate_id = request.POST.get("candidate")
        stream_id = request.POST.get("stream")
        committee_id = request.POST.get("committee")

        # Prevent admin from voting
        if request.user.is_staff or request.user.is_superuser:
            messages.error(request, "⚠️ Admin users are not allowed to vote.")
            return redirect(f"/voting/?stream={stream_id}&committee={committee_id}")

        # Candidate fetch
        candidate = get_object_or_404(Candidate, id=candidate_id)
        committee = get_object_or_404(Committee, pk=committee_id)

        # Prevent self-vote
        student_profile = getattr(request.user, "profile", None)  
        if student_profile and student_profile.roll_no == candidate.roll_no:
            messages.error(request, "⚠️ You cannot vote for yourself.")
            return redirect(f"/voting/?stream={stream_id}&committee={committee_id}")
        
        # Only vote in own stream/department
        if student_profile.department != committee.category:
            messages.error(request, "⚠️ You are not allowed to vote in this committee (different department).")
            return redirect(f"/voting/?stream={stream_id}&committee={committee_id}")

        # Check if voting is active
        if not committee.is_active:
            messages.error(request, "⚠️ Voting has not started for this committee yet.")
            return redirect(f"/voting/?stream={stream_id}&committee={committee_id}")

        # Check if already voted
        if Vote.objects.filter(user=request.user, committee=committee).exists():
            messages.error(request, "⚠️ You have already voted in this committee.")
        else:
            # Save vote
            Vote.objects.create(user=request.user, candidate=candidate, committee=committee)
            
            # Update result table automatically
            from .models import Result
            result, created = Result.objects.get_or_create(candidate=candidate, committee=committee)
            result.total_votes = Vote.objects.filter(candidate=candidate).count()
            result.save()

            messages.success(request, "✅ Your vote was recorded. Thank you!")

        #  Save committee in session (for result page)
        request.session["current_committee_id"] = committee.id

        return redirect(f"/voting/?stream={stream_id}&committee={committee_id}")  # No params, auto detect from session

    return redirect("category")


def login_view(request):
    if request.user.is_authenticated:  
        return redirect('index')      
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            StudentProfile.objects.create(
                user=user,
                department=form.cleaned_data["department"],
                year=form.cleaned_data["year"],
                division=form.cleaned_data["division"],
            )

            messages.success(request, "Your account has been created successfully! Please login.")
            return redirect("login")
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect('login')