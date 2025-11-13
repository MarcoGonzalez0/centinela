from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@mail.cl', 'admin')
    print("✅ Superusuario 'admin' creado automáticamente")
else:
    print("ℹ️ Superusuario 'admin' ya existe")
