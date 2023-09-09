# Generated by Django 4.1 on 2023-09-09 05:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('booking_id', models.AutoField(primary_key=True, serialize=False)),
                ('contractor_name', models.CharField(max_length=500)),
                ('contractor_email', models.EmailField(max_length=254)),
                ('labour_skill', models.CharField(max_length=500)),
                ('labour_count', models.IntegerField()),
                ('labour_gender', models.CharField(default='Male', max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('location', models.CharField(max_length=1000)),
                ('status', models.CharField(max_length=100)),
                ('amount', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Labour',
            fields=[
                ('first_name', models.CharField(max_length=500)),
                ('last_name', models.CharField(max_length=500)),
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=100)),
                ('skills', models.CharField(max_length=1000)),
                ('phone', models.CharField(max_length=10)),
                ('passport_no', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('booking_id', models.IntegerField()),
                ('payment_date', models.DateField()),
                ('amount', models.IntegerField()),
                ('status', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PublicHolidays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=1000)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('category', models.CharField(choices=[('General Workers', 'General Workers'), ('Skilled Workers', 'Skilled Workers')], default='General Workers', max_length=50)),
                ('skill', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('count', models.IntegerField()),
                ('cost_per_hour_normal_days', models.IntegerField()),
                ('cost_per_hour_public_holiday', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='LaboursAllocated',
            fields=[
                ('allocation_id', models.AutoField(primary_key=True, serialize=False)),
                ('labour_email', models.EmailField(max_length=254)),
                ('booking_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_services.booking')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('username', models.CharField(max_length=100, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('user_role', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('is_verified', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='last login')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
