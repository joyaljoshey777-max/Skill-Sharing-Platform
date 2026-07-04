from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Q
from .models import ProviderProfile, Skill, Booking, Review
from .forms import CustomerRegistrationForm, ProviderRegistrationForm

def home(request):
    return render(request, 'core/home.html')

def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. Welcome to SkillConnect!')
            return redirect('home')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'core/register_customer.html', {'form': form})

def register_provider(request):
    if request.method == 'POST':
        form = ProviderRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Your account is pending admin approval.')
            return redirect('login')
    else:
        form = ProviderRegistrationForm()
    return render(request, 'core/register_provider.html', {'form': form})

@login_required
def dashboard_redirect(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('/admin/')
    elif request.user.is_provider:
        return redirect('provider_dashboard')
    elif request.user.is_customer:
        return redirect('user_dashboard')
    return redirect('home')

def browse_skills(request):
    query = request.GET.get('q', '')
    providers = ProviderProfile.objects.filter(status='Approved')
    
    if query:
        providers = providers.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(skills__name__icontains=query)
        ).distinct()
        
    return render(request, 'core/browse.html', {
        'providers': providers,
        'query': query
    })

def provider_profile(request, provider_id):
    provider = get_object_or_404(ProviderProfile, id=provider_id, status='Approved')
    reviews = provider.reviews_received.all().order_by('-created_at')
    
    # Calculate average rating
    avg_rating = 0
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()
        
    return render(request, 'core/profile.html', {
        'provider': provider,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1)
    })

@login_required
def book_provider(request, provider_id):
    if not request.user.is_customer:
        messages.error(request, "Only customers can book providers.")
        return redirect('provider_profile', provider_id=provider_id)
        
    provider = get_object_or_404(ProviderProfile, id=provider_id, status='Approved')
    
    if request.method == 'POST':
        skill_id = request.POST.get('skill')
        date = request.POST.get('date')
        time = request.POST.get('time')
        message = request.POST.get('message', '')
        
        skill = get_object_or_404(Skill, id=skill_id, provider=provider)
        
        # Check if slot is already locked
        existing_booking = Booking.objects.filter(
            provider=provider, date=date, time=time, status='Confirmed'
        ).exists()
        
        if existing_booking:
            messages.error(request, "This provider is already booked at this time. Please select another time.")
        else:
            Booking.objects.create(
                user=request.user,
                provider=provider,
                skill=skill,
                date=date,
                time=time,
                message=message
            )
            messages.success(request, f"Booking request sent to {provider.user.first_name}!")
            return redirect('user_dashboard')
            
    return render(request, 'core/book.html', {'provider': provider})

@login_required
def user_dashboard(request):
    if not request.user.is_customer:
        return redirect('home')
        
    bookings = request.user.bookings.all().order_by('-date', '-time')
    return render(request, 'core/user_dashboard.html', {'bookings': bookings})

@login_required
def provider_dashboard(request):
    if not hasattr(request.user, 'provider_profile'):
        return redirect('home')
        
    profile = request.user.provider_profile
    bookings = profile.bookings_received.all().order_by('-date', '-time')
    
    pending = bookings.filter(status='Pending')
    upcoming = bookings.filter(status='Confirmed')
    completed = bookings.filter(status='Completed')
    
    return render(request, 'core/provider_dashboard.html', {
        'profile': profile,
        'pending': pending,
        'upcoming': upcoming,
        'completed': completed
    })

@login_required
def manage_booking(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id, provider__user=request.user)
    
    if action == 'accept':
        # Check slot again just in case
        conflict = Booking.objects.filter(
            provider=booking.provider, date=booking.date, time=booking.time, status='Confirmed'
        ).exists()
        
        if conflict:
            messages.error(request, "You already have a confirmed booking at this time.")
        else:
            booking.status = 'Confirmed'
            booking.save()
            # Also auto-reject other pending bookings for the same slot
            Booking.objects.filter(
                provider=booking.provider, date=booking.date, time=booking.time, status='Pending'
            ).update(status='Rejected')
            messages.success(request, "Booking accepted.")
            
    elif action == 'reject':
        if request.method == 'POST':
            booking.rejection_reason = request.POST.get('rejection_reason', '')
        booking.status = 'Rejected'
        booking.save()
        messages.success(request, "Booking rejected.")
        
    elif action == 'complete':
        if booking.status == 'Confirmed':
            booking.status = 'Completed'
            booking.save()
            messages.success(request, "Booking marked as completed.")
            
    return redirect('provider_dashboard')

@login_required
def submit_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='Completed')
    
    # Check if review already exists
    if Review.objects.filter(user=request.user, provider=booking.provider).exists():
        messages.error(request, "You have already reviewed this provider.")
        return redirect('user_dashboard')
        
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Review.objects.create(
                user=request.user,
                provider=booking.provider,
                rating=rating,
                comment=comment
            )
            messages.success(request, "Review submitted successfully!")
            return redirect('user_dashboard')
            
    return render(request, 'core/submit_review.html', {'booking': booking})
