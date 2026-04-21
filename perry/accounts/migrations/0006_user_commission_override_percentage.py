from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_user_profile_image_alter_user_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="commission_override_percentage",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="If set, overrides the tier percentage (e.g. 12.5 for 12.5%).",
                max_digits=5,
                null=True,
            ),
        ),
    ]

