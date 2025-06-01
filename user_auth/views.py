from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
from django.contrib.auth.models import User
import requests
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.helpers import complete_social_login


@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({"success": True})


def user_exist_check(request):
    username = request.GET.get('username')
    if User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "error": "使用者名稱已存在"})
    else:
        return JsonResponse({"success": True, "message": "用戶名可用"})


def api_login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({
            "success": True,
            "user": {"username": user.username, "email": user.email}
        })
    return JsonResponse({"success": False}, status=400)


def api_logout(request):
    logout(request)
    return JsonResponse({"success": True})


def check_auth_status(request):
    if request.user.is_authenticated:
        return JsonResponse({
            'isAuthenticated': True,
            'user': {
                'username': request.user.username,
                'email': request.user.email,
            }
        })
    else:
        return JsonResponse({'isAuthenticated': False})


def api_register(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')

    if User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "error": "使用者名稱已存在"}, status=400)

    user = User.objects.create_user(username=username, password=password)
    # login(request, user)
    return JsonResponse({
        "success": True,
        "user": {"username": user.username, "email": user.email}
    })

    if request.user.is_authenticated:
        return JsonResponse({
            "success": True,
            "user": {"username": request.user.username, "email": request.user.email}
        })
    return JsonResponse({"success": False}, status=401)


@csrf_exempt
def google_auth(request):
    """簡化版 Google 登入"""
    try:
        print("=== Google Auth Start ===")

        data = json.loads(request.body)
        access_token = data.get('access_token')

        if not access_token:
            return JsonResponse({
                'success': False,
                'error': '缺少 access_token'
            }, status=400)

        # 向 Google 驗證 token
        google_user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        response = requests.get(
            google_user_info_url,
            params={'access_token': access_token}
        )

        if response.status_code != 200:
            return JsonResponse({
                'success': False,
                'error': 'Google token 驗證失敗'
            }, status=400)

        google_user_data = response.json()
        email = google_user_data.get('email')
        google_id = google_user_data.get('id')

        print(f"Google user: {email}")

        # 找現有用戶或建立新用戶
        try:
            user = User.objects.get(email=email)
            action = 'login'
            print(f"現有用戶登入: {user.username}")
        except User.DoesNotExist:
            # 建立新用戶
            user = User.objects.create_user(
                username=google_user_data.get('name'),
                email=email
            )
            action = 'register'
            print(f"新用戶註冊: {user.username}")


        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return JsonResponse({
            'success': True,
            'action': action,
            'user': {
                'id': user.id,
                'username': google_user_data.get('name'),
                'email': user.email,
                'picture': google_user_data.get('picture'),
            }
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())

        return JsonResponse({
            'success': False,
            'error': f'錯誤: {str(e)}'
        }, status=500)